import logging
import os
import requests
import telegram

from dotenv import load_dotenv
from time import sleep


DVMN_URL = "https://dvmn.org/api/user_reviews/"
POLLING_URL = "https://dvmn.org/api/long_polling/"
TIMEOUT = 120
logger = logging.getLogger("dvmn-review-bot")


class TelegramLogsHandler(logging.Handler):
    def __init__(self, tg_bot: telegram.Bot, chat_id: int) -> None:
        super().__init__()
        self.tg_bot = tg_bot
        self.chat_id = chat_id

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def poll_for_new_reviews():
    headers = {
        "Authorization": os.environ['DVMN_TOKEN']
    }
    params = {
        "timestamp": None
    }
    bot = telegram.Bot(token=os.environ['TELEGRAM_TOKEN'])
    chat_id = os.environ['TELEGRAM_USER_ID']

    logger.addHandler(TelegramLogsHandler(bot, chat_id))
    logger.info("Бот запущен")
    while True:
        try:
            response = requests.get(POLLING_URL, headers=headers, timeout=TIMEOUT, params=params)
            response.raise_for_status()
            review_response = response.json()
            if review_response['status'] == 'timeout':
                params = {
                    "timestamp": review_response['timestamp_to_request']
                }
            elif review_response['status'] == 'found':
                logger.info("Бот получил новые ревью")
                for attempt in review_response['new_attempts']:
                    if attempt['is_negative']:
                        logger.info("Бот - преподаватель нашел ошибки в работе")
                        bot.send_message(
                            text=f'Преподаватель нашел ошибки в работе: \
                                   <a href="{attempt["lesson_url"]}">{attempt["lesson_title"]}</a>',
                            chat_id=chat_id,
                            parse_mode='HTML'
                            )
                    else:
                        logger.info("Бот - преподаватель проверил работу")
                        bot.send_message(
                            text=f'Преподаватель проверил работу: \
                                <a href="{attempt["lesson_url"]}">{attempt["lesson_title"]}</a>',
                            chat_id=chat_id,
                            parse_mode='HTML'
                            )
                params = {
                    "timestamp": review_response['last_attempt_timestamp']
                }
        except requests.exceptions.ReadTimeout:
            logger.warning("Бот - превышен таймаут")
            continue
        except requests.exceptions.ConnectionError:
            logger.warning("Бот - ошибка соединения")
            sleep(5)
            continue


if __name__ == "__main__":
    logger.setLevel(os.environ.get("LOGGING_LEVEL", "INFO"))
    load_dotenv()
    poll_for_new_reviews()
