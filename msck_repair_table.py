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