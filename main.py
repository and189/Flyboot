import json
import os
from dotenv import load_dotenv
import requests
import time
from datetime import datetime
from threading import Thread

from check_client import check_client

load_dotenv()

INTERVAL = int(os.getenv("INTERVAL"))

API_URL = os.getenv("API_URL")

with open('devices.json') as f:
    devices = json.load(f)

last_reboot = {}

def main():
    headers = {
        'Authorization': f'Bearer {os.getenv("API_TOKEN")}'
    }

    while True:
        print(f'Checking clients at {datetime.now()}...')

        response = requests.get(API_URL, headers=headers)
        client_status = response.json()

        threads = []
        for device in devices:
            thread = Thread(target=check_client, args=(device, client_status, last_reboot))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        print(f'Finished checking clients. Waiting for {INTERVAL} seconds...')

        time.sleep(INTERVAL)

if __name__ == '__main__':
    main()
