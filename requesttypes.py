
# This code sample uses the 'requests' library:
# http://docs.python-requests.org



#RETORNAR OS REQUESTTYPES PRESENTES NO SERVICE DESK
import requests
import json
import base64
from dotenv import load_dotenv
import os

load_dotenv()  # Carrega variáveis do .env

api_token = os.getenv('JIRA_TOKEN')
email_user = os.getenv('USER_EMAIL')


auth_str = f"{email_user}:{api_token}"
auth_bytes = auth_str.encode('ascii')
base64_bytes = base64.b64encode(auth_bytes)
base64_string = base64_bytes.decode('ascii')

url = "https://servicedeskleds.atlassian.net/rest/servicedeskapi/servicedesk/1/requesttype"

headers = {
    "Accept": "application/json",
    "Authorization": f"Basic {base64_string}"
}

response = requests.get(url, headers=headers)

print(json.dumps(response.json(), indent=4))
