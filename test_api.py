import requests
import json

url = "https://api.sheety.co/dce769ebe2f46d9d75105855f82a3d17/deisHacksWomenInBusinessEvent/formResponses1"

response = requests.get(url)
json_data = response.json()["formResponses1"]
print(json_data)
json_file = json.dumps(json_data)

with open("json_data/womeninbusiness.json", 'w') as file:
    file.write(json_file)
