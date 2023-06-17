import mysql.connector
import os
import requests
import subprocess
from datetime import datetime
import time

def check_client(device, client_status, last_reboot):
    DB_HOST = os.getenv("DB_HOST")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")
    RESTART_WAIT = int(os.getenv("RESTART_WAIT"))
    REBOOT_WAIT = int(os.getenv("REBOOT_WAIT"))
    ADBLOC = os.getenv("ADBLOC")
    API_URL = os.getenv("API_URL")
    MAD_RESTART_URL = os.getenv("MAD_RESTART_URL")

    uuid = device['uuid']
    mitm = device['MITM']
    ip = device['ip']

    print(f'Checking device {uuid}...')

    if any(device['uuid'] == uuid for device in client_status['data']):
        device_data = next(device for device in client_status['data'] if device['uuid'] == uuid)
        api_last_seen = datetime.fromtimestamp(device_data['last_seen'] / 1000)
        minutes_elapsed = (datetime.now() - api_last_seen).total_seconds() / 60

        if minutes_elapsed > RESTART_WAIT:
            print(f'Device {uuid} last seen {minutes_elapsed:.2f} minutes ago. Restarting...')

            restart_script = f'./restartskriptVMAPPER.sh'

            result = subprocess.run([restart_script, ADBLOC, ip], capture_output=True, text=True)

            db = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            cursor = db.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    uuid VARCHAR(255),
                    action VARCHAR(255),
                    success BOOLEAN,
                    timestamp TIMESTAMP
                )
            """)
            cursor.execute("ALTER TABLE logs ADD COLUMN IF NOT EXISTS success BOOLEAN")

            if result.returncode == 0:
                print(f'Device {uuid} restarted successfully.')
                cursor.execute("INSERT INTO logs (uuid, action, success, timestamp) VALUES (%s, %s, %s, %s)", (uuid,'restart', True ,datetime.now()))
            else:
                print(f'Device {uuid} restart failed.')
                cursor.execute("INSERT INTO logs (uuid, action, success, timestamp) VALUES (%s,%s,%s,%s)",(uuid,'restart', False ,datetime.now()))

            db.commit()
            cursor.close()
            db.close()

            print(f'Device {uuid} restarted. Waiting for {REBOOT_WAIT} minutes...')

            time.sleep(REBOOT_WAIT * 60)

            headers = {
                'Authorization': f'Bearer {os.getenv("API_TOKEN")}'
            }
            response = requests.get(API_URL, headers=headers)
            client_status = response.json()
            if not any(device['uuid'] == uuid for device in client_status['data']) or (any(device['uuid'] == uuid for device in client_status['data']) and (datetime.now() - datetime.fromtimestamp(next(device for device in client_status['data'] if device['uuid'] == uuid)['last_seen'] / 1000)).total_seconds() / 60 > RESTART_WAIT):
                print(f'Device {uuid} still offline. Rebooting...')

                if uuid not in last_reboot or (datetime.now() - last_reboot[uuid]).total_seconds() > 10 * 60:
                    # Starte das Reboot-Skript mit dem ADB-Pfad und der entsprechenden IP
                    result = subprocess.run(['./rebootskript.sh', ADBLOC, ip], capture_output=True, text=True)

                    db = mysql.connector.connect(
                        host=DB_HOST,
                        user=DB_USER,
                        password=DB_PASSWORD,
                        database=DB_NAME
                    )
                    cursor = db.cursor()

                    if result.returncode == 0:
                        print(f'Device {uuid} rebooted successfully.')
                        cursor.execute("INSERT INTO logs (uuid, action, success, timestamp) VALUES (%s, %s, %s, %s)", (uuid,'reboot', True ,datetime.now()))
                    else:
                        print(f'Device {uuid} reboot failed.')
                        cursor.execute("INSERT INTO logs (uuid, action, success, timestamp) VALUES (%s,%s,%s,%s)",(uuid,'reboot', False ,datetime.now()))

                    db.commit()
                    cursor.close()
                    db.close()

                    if mitm == "MAD1":
                        restart_url = MAD_RESTART_URL.replace("UUID", uuid)
                        requests.get(restart_url)

                    last_reboot[uuid] = datetime.now()

