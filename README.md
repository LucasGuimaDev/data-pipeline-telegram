# data-pipeline-telegram

O [telegram](https://pt.wikipedia.org/wiki/Telegram) é uma famosa rede social de mensagens que está ativa no mercado desde 2013 e desde então se tornou uma fonte rica de diversos tipos de dados

-----

## Contexto
O projeto a seguir consiste na criação de um pipeline que coleta esses dados através de um chatbot alocado em um grupo e torna-os em dados visíveis que podem, futuramente, se tornar insights valiosos. 

Chatbot é um robô conversacional que oferece respostas aos usuários e é com ele que faremos as coletas de todas as mensagens.

As mensagens enviadas no grupo e coletadas pelo chatbot são dados transacionais, ou seja, são dados brutos, sem nenhum tipo de tratamento e que muitas vezes cotém informações irrelevantes para determinada análise.

Os dados transacionais passarão pelo processo de ETL para então se tornarem dados analíticos. Dados analíticos por sua vez, são dados tratados de uma forma que podem ser utilizados em análises.

-----

## Fluxograma do pipeline dos dados
![fluxograma](https://github.com/LucasGuimaDev/data-pipeline-telegram/blob/main/imagens/fluxograma_data_pipeline.png)


O chat bot faz a leitura dos dados transacionais, ou melhor dizendo, as mensagens enviadas pelos usuários no grupo do telegram,  e através do API Gateway e do AWS Lambda elas são salvas em um bucket no AWS S3 no formato json

----

## Bot Telegram


Após criar o bot no telegram atravé do BotFather ele mostrará o *token* de acesso, caso não tenha anotado, segue passo a passo para buscar esse toke

*Lembre-se, esse token é confidencial, portanto,  não o compartilhe*

Para acessar o *token* basta mandar a menssagem */mybots* para o BotFather, selecionar o bot criado e então acessar a aba *API Token*, como demonstrado abaixo:

![screen_shot_1](https://github.com/LucasGuimaDev/data-pipeline-telegram/blob/main/imagens/print1.png)



O *token* de acesso é um código que aparece logo abaixo do nome do bot na cor laranja

![screen_shoot_2](https://github.com/LucasGuimaDev/data-pipeline-telegram/blob/main/imagens/print2.png)

*Após adicionar o bot no grupo de coleta de dados, lembre-se de desabilitar a adição do bot em grupos*

-----
Após coletar os *token* de acesso insira ele na variável "token" usando o método getpass:

*Este método é essencial para se trabalhar com dados confidenciais.*

```python
from getpass import getpass

token = getpass()
```
Passando o *token* de acesso para a variável, passamos o valor para a URL da API e então com a lib *requests* e o acessamos as informações com o método getMe como no código abaixo:
```python
import json
import requests

base_url = f'https://api.telegram.org/bot{token}'

response = requests.get(url=f'{base_url}/getMe')

print(json.dumps(json.loads(response.text), indent=2))
```
o método getMe retorna um json com as seguintes informações:
```python
{
  "ok": true,
  "result": {
    "id": ******,
    "is_bot": true,
    "first_name": "*****",
    "username": "******",
    "can_join_groups": false,
    "can_read_all_group_messages": false,
    "supports_inline_queries": false,
    "can_connect_to_business": false
  }
}
```
Para analisar as mensagens envidas no grupo e captadas pelo bot existe um outro método chamado *getUpdates*

```python
response = requests.get(url=f'{base_url}/getUpdates')

print(json.dumps(json.loads(response.text), indent=2))
```
Este método retorna um json com as seguintes informações:
```python
{
  "ok": true,
  "result": [
    {
      "update_id": *****,
      "message": {
        "message_id": 5,
        "from": {
          "id": *****,
          "is_bot": false,
          "first_name": "Lucas",
          "last_name": "Guimar\u00e3es",
          "language_code": "pt-br"
        },
        "chat": {
          "id": -10*****,
          "title": "Gru****",
          "type": "supergroup"
        },
        "date": 1719956510,
        "text": "teste"
      }
    }
  ]
}
```
Neste json é possível captar o tipo de mensagem enviada, quem enviou, a data da mensagem, o tipo do grupo e o ID desse respectivo grupo.

A informação mais importante nestes dados é o *id* do grupo que está localizado nesta parte do código:
```python
"chat": {
  "id": -10*****,
  "title": "Gru****",
  "type": "supergroup"
}
```

Este *id* será utilizado na variável de ambiente **TELEGRAM_CHAT_ID**

----
## Ingestão de dados

Feito a criação do grupo e da verificação dos dados do bot, criaremos um bucket no S3 com o sufixo -raw para salvar todas as mensagens em formato json e criaremos uma função através do AWS Lambda para salvar os dados nesse bucket. Não se esqueça de configurar as variáveis de ambiente e de adicionar as permissão de interação com AWS S3 no AWS IAM.

Segue a função para realizar a ingestão dos dados transacionais em formato json para o bucket no S3:

```python
import os
import json
import logging
from datetime import datetime, timedelta, timezone

import boto3


def lambda_handler(event: dict, context: dict) -> dict:

  '''
  Recebe uma mensagens do Telegram via AWS API Gateway, verifica no
  seu conteúdo se foi produzida em um determinado grupo e a escreve,
  em seu formato original JSON, em um bucket do AWS S3.
  '''

  # vars de ambiente

  BUCKET = os.environ['AWS_S3_BUCKET']
  TELEGRAM_CHAT_ID = int(os.environ['TELEGRAM_CHAT_ID'])

  # vars lógicas

  tzinfo = timezone(offset=timedelta(hours=-3))
  date = datetime.now(tzinfo).strftime('%Y-%m-%d')
  timestamp = datetime.now(tzinfo).strftime('%Y%m%d%H%M%S%f')

  filename = f'{timestamp}.json'

  # código principal

  client = boto3.client('s3')

  try:

    message = json.loads(event["body"])
    chat_id = message["message"]["chat"]["id"]

    if chat_id == TELEGRAM_CHAT_ID:

      with open(f"/tmp/{filename}", mode='w', encoding='utf8') as fp:
        json.dump(message, fp)

      client.upload_file(f'/tmp/{filename}', BUCKET, f'telegram/context_date={date}/{filename}')

  except Exception as exc:
      logging.error(msg=exc)
      return dict(statusCode="500")

  else:
      return dict(statusCode="200")

```


