import os
import requests

from dotenv import load_dotenv
from time import sleep

load_dotenv()


DVMN_URL = "https://dvmn.org/api/user_reviews/"
POLLING_URL = "https://dvmn.org/api/long_polling/"
TIMEOUT = 5


def poll_for_new_reviews():
    headers = {
        "Authorization": os.environ['DVMN_TOKEN']
    }
    while True:
        try:
            response = requests.get(POLLING_URL, headers=headers, timeout=TIMEOUT)
        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            sleep(5)
            continue
        response.raise_for_status()
        print(response.json())


def main():
    headers = {
        "Authorization": os.environ['DVMN_TOKEN']
    }
    response = requests.get(DVMN_URL, headers=headers)
    print(response.json())


if __name__ == "__main__":
    main()
    poll_for_new_reviews()
