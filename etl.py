# import libraries
from util import get_redshift_connection,\
execute_sql, list_files_in_folder
import pandas as pd
import requests
import boto3
from datetime import datetime
from io import StringIO
import io
import psycopg2
import ast
from dotenv import dotenv_values
dotenv_values()

# Get credentials from environment variable file
config = dotenv_values('.env')

# Create a boto3 s3 client for bucket operations
s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')

def get_data_from_api():
    url = config.get('URL')
    headers = ast.literal_eval(config.get('HEADERS'))
    querystring = ast.literal_eval(config.get('QUERYSTRING'))
    try:
        # Send request to Rapid API and return the response as a Json object
        response = requests.get(url, headers=headers, params=querystring).json()
    except ConnectionError:    
        print('Unable to connect to the URL endpoint')
    coin_data = response.get('data').get('coins')
    columns = ['symbol', 'name', 'price', 'rank','btcPrice', 'lowVolume']
    crypto_price_data = pd.DataFrame(coin_data)[columns]
    return crypto_price_data




def transform_data(data):
    data['price'] = data['price'].apply(lambda x: float(x)) # convert string column to float value
    data['date'] = datetime.now().strftime('%Y-%m-%d-%H-%M-%S') # Add a date column
    data['date'] = pd.to_datetime(data['date'], format ='%Y-%m-%d-%H-%M-%S')
    data = data[['date', 'symbol', 'name', 'price', 'rank','btcPrice', 'lowVolume']]
    return data


def load_to_redshift(bucket_name, folder, redshift_table_name):
    iam_role = config.get('IAM_ROLE')
    conn = get_redshift_connection()
    file_paths = [f's3://{bucket_name}/{file_name}' for file_name in list_files_in_folder(bucket_name, folder)]
    for file_path in file_paths:
        copy_query = f"""
        copy {redshift_table_name}
        from '{file_path}'
        IAM_ROLE '{iam_role}'
        csv
        IGNOREHEADER 1;
        """
        execute_sql(copy_query, conn)
    print('Data successfully loaded to Redshift')
    
