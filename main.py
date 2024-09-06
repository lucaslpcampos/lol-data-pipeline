import requests
import pandas as pd
import json
import os
import time
import datetime
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

with open('header.json', 'r') as file:
    file_content = file.read()
    headers = json.loads(file_content)

# Acessa a variável de ambiente
api_key = os.getenv('API_KEY')

account_api_url = r'https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id'

def get_account_puuid(api_url:str, user_name: list, user_tag: list, api_key:str, headers) -> dict:
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
        response = requests.get(f'{account_api_url}',headers=headers)
        data = response.json()
        account_details[f'{user}_{tag}'] = data
    return account_details

summoner_api_url = f'https://br1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid'

def get_summoner_id(api_url:str, account_details:dict, api_key:str, headers, server='br1') -> dict:
    '''
    Get summoner id by puuid
    '''
    if server != 'br1':
        api_url.replace('br1',server)
    summoner_details = {}
    for user in account_details.items():
        puuid = user[1]['puuid']
        summoner_api_url = f'{api_url}/{puuid}?api_key={api_key}'
        response = requests.get(f'{summoner_api_url}',headers=headers)
        data = response.json()
        summoner_details[user[0]] = data
    return summoner_details

matches_api_url = f'https://americas.api.riotgames.com/lol/match/v5/matches'

def get_match_id(api_url: str, account_details: dict, start_time: str, end_time: str, type_queue: str, start: int, count: int, api_key: str, headers) -> dict:
    matches_id = {}
    start_time = convert_to_epoch(start_time)
    end_time = convert_to_epoch(end_time)
    
    for user in account_details.items():
        puuid = user[1]['puuid']
        matches_id[user[0]] = []  # Inicializa uma lista para cada usuário
        
        # Reinicializa o valor de `start` para cada novo usuário
        current_start = start
        done = False  # Variável de controle para terminar o while

        while not done:
            matches_api_url = (
                f'{api_url}/by-puuid/{puuid}/ids?startTime={start_time}&endTime={end_time}'
                f'&type={type_queue}&start={current_start}&count={count}&api_key={api_key}'
            )
            response = requests.get(matches_api_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if not data:
                    done = True  # Finaliza o loop while quando não há mais dados
                else:
                    matches_id[user[0]].extend(data)  # Acumula partidas
                    current_start += count  # Incrementa o `start` apenas para este usuário
            else:
                print(f'Erro {response.status_code} para o usuário {user[0]}')
                done = True  # Finaliza o loop while em caso de erro
    
    return matches_id

def convert_to_epoch(date_str):
    # Verifica se a data está no formato DD/MM/YYYY
    try:
        date_obj = datetime.datetime.strptime(date_str, "%d/%m/%Y")
        # Converte para Epoch timestamp em segundos
        return int(date_obj.timestamp())
    except ValueError:
        return "Formato de data inválido. Use o formato DD/MM/YYYY."

def get_champions_details(api_url= 'https://ddragon.leagueoflegends.com/cdn/14.17.1/data/en_US/champion.json') -> json:
    data = requests.get(url=api_url)
    return data.json()

def get_match_details(api_url: str, matches_id: dict, api_key: str, headers):
    match_details = {}
    for details in matches_id.items():
        user = details[0]
        for match in details[1]:
            url = f'{api_url}/{match}?api_key={api_key}'
            response = requests.get(url=url, headers=headers)
            data = response.json()
            match_details[user]=data
    return match_details

account_details = get_account_puuid(api_url=account_api_url, user_name=['pipita','meetu'], user_tag=['br1','mtu'],api_key=api_key,headers=headers)

matches_id = get_match_id(api_url=matches_api_url, account_details=account_details,start_time="01/08/2024", end_time="05/08/2024", type_queue='ranked',start=0, count=20, api_key=api_key, headers=headers)

summoner_details = get_summoner_id(api_url=summoner_api_url, account_details=account_details, api_key=api_key, headers=headers)

match_details = get_match_details(api_url=matches_api_url,matches_id=matches_id,api_key=api_key,headers=headers)

print(match_details)