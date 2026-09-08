import requests
import json
import os




url = "https://app.metricool.com/api/v2/analytics/posts/instagram?blogId=5784679&userId=5193289"
parameters = {
        "from" : '2026-07-01T00:00:00',
        "to" : '2026-08-31T00:00:00',
        "timezone" : 'America/New_York' 
    }

response = requests.get(url=url, headers={"X-Mc-Auth": os.environ.get("METRICOOL_KEY")}, params=parameters)

data = ""
if response.status_code == 200:
    data = response.json()
else:
    print(response.status_code)

with open("data.txt", "w") as file:
    file.write(str(data))
    
