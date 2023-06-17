import json
import requests

API_URL = "http://192.168.1.211:9002/api/workers/?perPage=1000"
API_TOKEN = "your_api_token_here"

headers = {'Authorization': 'Bearer ' + API_TOKEN}

# Lese die vorhandenen Geräteinformationen aus der devices2.json-Datei ein
with open('devices.json') as f:
    devices = json.load(f)

# Hole neue Geräteinformationen von der API
response = requests.get(API_URL, headers=headers)
data = response.json()

# Füge neue Geräte zur Liste hinzu, ohne vorhandene Einträge zu löschen oder doppelte Einträge hinzuzufügen
# ersetze Proxy_IP durch  MAD1 api curl call / change IP 10.7.0.1  
for device in data['data']:
    if not any(d['uuid'] == device['uuid'] for d in devices):
        if device['host'] == '10.7.0.1':
            devices.append({'uuid': device['uuid'], 'ip': device['host'], 'MITM': 'MAD1'})
        else:
            devices.append({'uuid': device['uuid'], 'ip': device['host'], 'MITM': 'VMAPPER'})

# Schreibe die aktualisierte Liste in die devices2.json-Datei
with open('devices.json', 'w') as f:
    json.dump(devices, f, indent=4)
