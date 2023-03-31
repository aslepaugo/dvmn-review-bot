import os
import requests
import telegram

from dotenv import load_dotenv
from time import sleep


DVMN_URL = "https://dvmn.org/api/user_reviews/"
POLLING_URL = "https://dvmn.org/api/long_polling/"
TIMEOUT = 120


def poll_for_new_reviews():
    headers = {
        "Authorization": os.environ['DVMN_TOKEN']
    }
    params = {
        "timestamp": None
    }
    bot = telegram.Bot(token=os.environ['TELEGRAM_TOKEN'])
    chat_id = os.environ['TELEGRAM_USER_ID']    
    while True:
        try:
            response = requests.get(POLLING_URL, headers=headers, timeout=TIMEOUT, params=params)
            if response.json()['status'] == 'timeout':
                params = {
                    "timestamp": response.json()['timestamp_to_request']
                }
            elif response.json()['status'] == 'found':
                for attempt in response.json()['new_attempts']:
                    if attempt['is_negative']:
                        bot.send_message(
                            text=f'Преподаватель нашел ошибки в работе: \
                                   <a href="{attempt["lesson_url"]}">{attempt["lesson_title"]}</a>',
                            chat_id=chat_id,
                            parse_mode='HTML'
                            )
                    else:
                        bot.send_message(
                            text=f'Преподаватель проверил работу: \
                                <a href="{attempt["lesson_url"]}">{attempt["lesson_title"]}</a>',
                            chat_id=chat_id,
                            parse_mode='HTML'
                            )
                params = {
                    "timestamp": response.json()['last_attempt_timestamp']
                }
        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            sleep(5)
            continue

        response.raise_for_status()


if __name__ == "__main__":
    load_dotenv()
    poll_for_new_reviews()
