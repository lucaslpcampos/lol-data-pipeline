import requests
import pandas as pd
import json
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

with open('header.json', 'r') as file:
    file_content = file.read()
    headers = json.loads(file_content)

# Acessa a variável de ambiente
api_key = os.getenv('API_KEY')

account_api_url = r'https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id'

def get_account_api(api_url:str, user_name: list, user_tag: list, api_key:str, headers) -> dict:
    '''
    Get puuid from player name and tag
    param api_url: api of riot account api
    param user_name: list of player's user name to request the id
    param user_tag: list of player's tag to request the id
    param api_key: api_key to autenticate the request
    param headers: headers
    '''
    account_details = {}
    for user, tag in zip(user_name, user_tag):
        account_api_url = f'{api_url}/{user}/{tag}?api_key={api_key}'
        print(account_api_url)
        response = requests.get(f'{account_api_url}',headers=headers)
        data = response.json()
        account_details[f'{user}_{tag}'] = data
    return account_details

account_details = get_account_api(api_url=account_api_url, user_name=['pipita','meetu'], user_tag=['br1','mtu'],api_key=api_key,headers=headers)
