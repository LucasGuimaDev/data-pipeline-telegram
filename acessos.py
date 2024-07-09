'''

código para acessar o token do telegram

'''

import json
import requests
from getpass import getpass

token = getpass()

base_url = f'https://api.telegram.org/bot{token}'

response = requests.get(url=f'{base_url}/getMe')

print(json.dumps(json.loads(response.text), indent=2))

response = requests.get(url=f'{base_url}/getUpdates')

print(json.dumps(json.loads(response.text), indent=2))

'''------------------------------------------'''

'''
Código para acessar a API do AWS API Gateway e setar o webhook

'''

from getpass import getpass
aws_api_gateway_url = getpass()

import requests
response = requests.get(url=f'{base_url}/setWebhook?url={aws_api_gateway_url}')

print(json.dumps(json.loads(response.text), indent=2))


'''------------------------------------------'''
