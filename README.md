# data-pipeline-telegram

O [telegram](https://pt.wikipedia.org/wiki/Telegram) é uma famosa rede social de mensagens que está ativa no mercado desde 2013 e desde então se tornou uma fonte rica de diversos tipos de dados

-----

## Contexto
O projeto a seguir consiste na criação de um pipeline que coleta esses dados através de um chatbot alocado em um grupo e torna-os em dados visíveis que podem, futuramente, se tornar insights valiosos. 

Chatbot é um robô conversacional que oferece respostas aos usuários e é com ele que faremos as coletas de todas as mensagens.

As mensagens enviadas no grupo e coletadas pelo chatbot são dados transacionais, ou seja, são dados brutos, sem nenhum tipo de tratamento e que muitas vezes cotém informações irrelevantes para determinada análise.

Os dados transacionais passarão pelo processo de ETL para então se tornarem dados analíticos. Dados analíticos por sua vez, são dados tratados de uma forma que podem ser utilizados em análises.

Os serviços utilizados nesse pipeline são oferecidos pela [AWS](https://aws.amazon.com/pt/?nc2=h_lg) mais especificamente o [AWS Lambda](https://aws.amazon.com/pt/lambda/) para realizar as funções, [AWS S3](https://aws.amazon.com/pt/s3/) para o armazenamento de dados, [AWS Gateway](https://aws.amazon.com/pt/api-gateway/) para criação da API, [AWS IAM](https://aws.amazon.com/pt/iam/) para liberar os acessos das funções aos outros serviços,[AWS EventBridge](https://aws.amazon.com/pt/eventbridge/) para rodar as funções sempre em um determinado horário e o [AWS Athena](https://aws.amazon.com/pt/athena/) para visualização dos dados em formato de tabela e consulta **SQL**.

-----

## Fluxograma do pipeline dos dados
![fluxograma](https://github.com/LucasGuimaDev/data-pipeline-telegram/blob/main/imagens/fluxograma_data_pipeline.png)


O chat bot faz a leitura dos dados transacionais, ou melhor dizendo, as mensagens enviadas pelos usuários no grupo do telegram,  e através do `API Gateway` e do `AWS Lambda` elas são salvas em um bucket no `AWS S3` no formato json

----

## Bot Telegram


Após criar o bot no telegram atravé do `BotFather` ele mostrará o `token` de acesso, caso não tenha anotado, segue passo a passo para buscar esse `token`

*Lembre-se, esse `token` é confidencial, portanto,  não o compartilhe*

Para acessar o `token` basta mandar a menssagem `/mybots` para o `BotFather`, selecionar o bot criado e então acessar a aba `API Token`, como demonstrado abaixo:

![screen_shot_1](https://github.com/LucasGuimaDev/data-pipeline-telegram/blob/main/imagens/print1.png)



O `token` de acesso é um código que aparece logo abaixo do nome do bot na cor laranja

![screen_shoot_2](https://github.com/LucasGuimaDev/data-pipeline-telegram/blob/main/imagens/print2.png)

*Após adicionar o bot no grupo de coleta de dados, lembre-se de `desabilitar` a adição do bot em grupos*

-----
Após coletar os `token` de acesso insira ele na variável "token" usando o método getpass:

*Este método é essencial para se trabalhar com dados confidenciais.*

```python
from getpass import getpass

token = getpass()
```
Passando o `token` de acesso para a variável, passamos o valor para a URL da API e então com a lib `requests` e o acessamos as informações com o método `getMe` como no código abaixo:
```python
import json
import requests

base_url = f'https://api.telegram.org/bot{token}'

response = requests.get(url=f'{base_url}/getMe')

print(json.dumps(json.loads(response.text), indent=2))
```
o método `getMe` retorna um json com as seguintes informações:
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
Para analisar as mensagens envidas no grupo e captadas pelo bot existe um outro método chamado `getUpdates`

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

A informação mais importante nestes dados é o `id` do grupo que está localizado nesta parte do código:
```python
"chat": {
  "id": -10*****,
  "title": "Gru****",
  "type": "supergroup"
}
```

Este `id` será utilizado na variável de ambiente `TELEGRAM_CHAT_ID`.

----
## Ingestão de dados

Feito a criação do grupo e da verificação dos dados do bot, criaremos um bucket no `AWS S3` com o sufixo `-raw` para salvar todas as mensagens em formato json e criaremos uma função através do `AWS Lambda` para salvar os dados nesse bucket. Os dados serão separados de acordo com as datas das mensagens. Não se esqueça de configurar as variáveis de ambiente e de adicionar as permissão de interação com `AWS S3` no `AWS IAM`.

Segue a função para realizar a ingestão dos dados transacionais em formato json para o bucket:

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

----

## API Gateway

Depois de criar a função lambda é necessário criar uma APi através do `AWS API Gateway` para coletar as mensagens que serão enviadas no grupo automaticamente, conectar a função lambda criada e posteriormente setar um `webhook` para realizar essa coleta. O webhook irá coletar esses dados e então passar eles pela função Lambda que acaba de ser criada.

O `AWS API Gateway` gera um endereço de API, portanto utilizaremos o getpass para coletar essa informação

*O endereço do API gateway é confidencial*

```python
from getpass import getpass
aws_api_gateway_url = getpass()
```

A partir disso iremos setar o `webhook`:

```python
import requests
response = requests.get(url=f'{base_url}/setWebhook?url={aws_api_gateway_url}')

print(json.dumps(json.loads(response.text), indent=2))
```

Estas linhas de código irão criar o webhook a partir do endereço da API criada.

A seguinte mensagem deve aparecer:

```python
{
  "ok": true,
  "result": true,
  "description": "Webhook was set"
}
```
Neste caso o webhook foi criado corretamente.

Caso queira mais informações sobre o webhook:
```python
{
  "ok": true,
  "result": {
    "url": "https://*******",
    "has_custom_certificate": false,
    "pending_update_count": 0,
    "max_connections": 40,
    "ip_address": "5**********"
  }
}
```

------

## ETL

Na parte de ETL criaremos novamente um bucket no `AWS S3` para armazenarmos os dados tratados, esse bucket deve conter o sufixo `-enriched`.

Para salvar esses dados novamente iremos criar uma função no `AWS Lambda` para processar os dados `json` de uma única partição do dia anterior (D-1) que estão armazenadas no bucket com os dados crus. Lembre-se de novmamente configurar as variáveis de ambiente corretas e de adicionar as permissões através do `AWS IAM`. Neste caso em específico se faz necessário configurar um *`timeout`* maior, por padrão o `AWS Lambda` vem com um tempo de 3 segundos para procesar a função, por se tratar de muitos dados esse número deve ser maior, recomenda-se um *`timeout`* de 5 minutos para que tenha tempo o suficiente. Além do *timeout*, nesse caso a função que iremos utilizar contém algumas bibliotecas que não estão dentro do ambiente de execução do `AWS Lambda`, que é o caso do *`pyarrow`*, portanto é necessário adicionar uma *`layer`* com o código desse pacote. O próprio `AWS Lambda` ja oferece uma *`layer`* com esse pacote, chamada `AWSSDKPandas-Python39`.

Segue abaixo a função:

```python
import os
import json
import logging
from datetime import datetime, timedelta, timezone

import boto3
import pyarrow as pa
import pyarrow.parquet as pq


def lambda_handler(event: dict, context: dict) -> bool:

  '''
  Diariamente é executado para compactar as diversas mensagensm, no formato
  JSON, do dia anterior, armazenadas no bucket de dados cru, em um único
  arquivo no formato PARQUET, armazenando-o no bucket de dados enriquecidos
  '''

  # vars de ambiente

  RAW_BUCKET = os.environ['AWS_S3_BUCKET'] # link do bucket com os dados crus, com sufixo -raw
  ENRICHED_BUCKET = os.environ['AWS_S3_ENRICHED'] # link do bucket com os dados tratados, com sufixo -enriched

  # vars lógicas

  tzinfo = timezone(offset=timedelta(hours=-3))
  date = (datetime.now(tzinfo) - timedelta(days=1)).strftime('%Y-%m-%d')
  timestamp = datetime.now(tzinfo).strftime('%Y%m%d%H%M%S%f')

  # código principal

  table = None
  client = boto3.client('s3')

  try:

      response = client.list_objects_v2(Bucket=RAW_BUCKET, Prefix=f'telegram/context_date={date}')

      for content in response['Contents']:

        key = content['Key']
        client.download_file(RAW_BUCKET, key, f"/tmp/{key.split('/')[-1]}")

        with open(f"/tmp/{key.split('/')[-1]}", mode='r', encoding='utf8') as fp:

          data = json.load(fp)
          data = data["message"]

        parsed_data = parse_data(data=data)
        iter_table = pa.Table.from_pydict(mapping=parsed_data)

        if table:

          table = pa.concat_tables([table, iter_table])

        else:

          table = iter_table
          iter_table = None

      pq.write_table(table=table, where=f'/tmp/{timestamp}.parquet')
      client.upload_file(f"/tmp/{timestamp}.parquet", ENRICHED_BUCKET, f"telegram/context_date={date}/{timestamp}.parquet")

      return True

  except Exception as exc:
      logging.error(msg=exc)
      return False


def parse_data(data: dict) -> dict:

  date = datetime.now().strftime('%Y-%m-%d')
  timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

  parsed_data = dict()

  for key, value in data.items():

      if key == 'from':
          for k, v in data[key].items():
              if k in ['id', 'is_bot', 'first_name']:
                parsed_data[f"{key if key == 'chat' else 'user'}_{k}"] = [v]

      elif key == 'chat':
          for k, v in data[key].items():
              if k in ['id', 'type']:
                parsed_data[f"{key if key == 'chat' else 'user'}_{k}"] = [v]

      elif key in ['message_id', 'date', 'text']:
          parsed_data[key] = [value]

  if not 'text' in parsed_data.keys():
    parsed_data['text'] = [None]

  return parsed_data
```
-----
## AWS EventBridge


Para rodar a função `AWS Lambda` todo dia em um determinado horário foi utilizado uma regra criada no `AWS EventBridge` que roda essa função todos os dias às 3h da manhã.
Lembrando que a função correta é a que busca os dados no bucket com o sufixo `-raw`, faz o processo de tratamento e os salva no bucket com o sufixo `-enriched`.


----

## AWS Athena

Para visualizar os dados utilizamos o `AWS Athena` a partir da query abaixo:
```sql
CREATE EXTERNAL TABLE `telegram_datalake`(
  `message_id` bigint,
  `user_id` bigint,
  `user_is_bot` boolean,
  `user_first_name` string,
  `chat_id` bigint,
  `chat_type` string,
  `text` string,
  `date` bigint)
PARTITIONED BY (
  `context_date` date)
ROW FORMAT SERDE
  'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe'
STORED AS INPUTFORMAT
  'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat'
OUTPUTFORMAT
  'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat'
LOCATION
  's3://<bucket-enriquecido>/'
```
A query `SQL` cria uma tabela chamada `telegram_datalake` com os dados do bucket com sufixo `-enriched`.

Toda vez que uma nova partição é adicionada ao repositório de dados é necessário informar ao `AWS Athena` para que esse dados estejam disponíveis para a visualização, sendo assim vamos utilizar um comando chamado `MSCK REPAIR TABLE <nome-tabela>`, documentação neste [link](https://docs.aws.amazon.com/athena/latest/ug/alter-table-add-partition.html).

```sql
MSCK REPAIR TABLE `telegram_datalake`;
```
É possível automatizar esse processo criando uma função no `AWS Lambda` e posteriormente um evento no `AWS EventBridge`.

*Lembre-se de dar os acessos necessários através do `AWS IAM`, configurar as variáveis de ambiente, adicionar a `Layer` para que a função funcione corretamente e configurar o evento no `AWS EventBridge` ao menos 30 minutos depois do que foi configurado o evento anterios, para que dê tempo o suficiente da função lambda carregar os dados tratado no bucket `-enriched`*.

```python
import os
import json
import boto3
import time

def lambda_handler(event, context):
    # Inicializa os clientes do boto3
    athena_client = boto3.client('athena')

    # Configurações da execução da query
    query = "MSCK REPAIR TABLE `telegram_datalake`;"
    database = os.environ['DATABASE']  # Substitua pelo nome do seu banco de dados no Athena
    output_location = os.environ['AWS_S3_BUCKET']  # Substitua pelo caminho do seu bucket S3

    try:
        # Executa a query
        response = athena_client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={
                'Database': database
            },
            ResultConfiguration={
                'OutputLocation': output_location
            }
        )

        # Pega o ID da execução da query
        query_execution_id = response['QueryExecutionId']

        # Espera até que a consulta seja concluída
        while True:
            query_status = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
            status = query_status['QueryExecution']['Status']['State']

            if status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
                break

            time.sleep(1)  # Aguarda 1 segundo antes de verificar novamente

        if status == 'SUCCEEDED':
            return {
                'statusCode': 200,
                'body': json.dumps('Query succeeded')
            }
        else:
            # Obtenha mais informações sobre a falha
            reason = query_status['QueryExecution']['Status'].get('StateChangeReason', 'Unknown')
            return {
                'statusCode': 500,
                'body': json.dumps(f'Query failed with status: {status}. Reason: {reason}')
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error executing query: {str(e)}')
        }
```
----

## Conclusão


E por fim, teremos todos os dados salvos em uma tabela no `AWS Athena` para futuras análises, a partir do `AWS Athena` podemos realizar queries em formato `SQL` como por exeplo:

Para visualizar todas as informações da tabela:
```sql
SELECT * FROM `telegram_datalake`;
```

Para visualizar a quantidade de mensagens por usuário por dia:

```sql
SELECT
  user_id,
  user_first_name,
  context_date,
  count(1) AS "message_amount"
FROM "telegram_datalake"
GROUP BY
  user_id,
  user_first_name,
  context_date
ORDER BY context_date DESC
```
E então podemos realizar o *download* das informações das queries em formato `.csv`
