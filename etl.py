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



def read_from_s3(bucket_name, path):
    objects_list = s3_client.list_objects(Bucket = bucket_name, Prefix = path) # List the objects in the bucket
    file = objects_list.get('Contents')[1]
    key = file.get('Key') # Get file path or key
    obj = s3_client.get_object(Bucket = bucket_name, Key= key)
    data = pd.read_csv(io.BytesIO(obj['Body'].read()))
    return data


def read_multi_files_from_s3(bucket_name, prefix):
    objects_list = s3_client.list_objects(Bucket = bucket_name, Prefix = prefix) # List the objects in the bucket
    files = objects_list.get('Contents')
    keys = [file.get('Key') for file in files][1:]
    objs = [s3_client.get_object(Bucket = bucket_name, Key= key) for key in keys]
    dfs = [pd.read_csv(io.BytesIO(obj['Body'].read())) for obj in objs]
    data = pd.concat(dfs)
    return data

def write_to_s3(data, bucket_name, folder):
    file_name = f"crypto_price_data_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.csv" # Create a file name
    csv_buffer = StringIO() # Create a string buffer to collect csv string
    data.to_csv(csv_buffer, index=False) # Convert dataframe to CSV file and add to buffer
    csv_str = csv_buffer.getvalue() # Get the csv string
    # using the put_object(write) operation to write the data into s3
    s3_client.put_object(Bucket=bucket_name, Key=f'{folder}/{file_name}', Body=csv_str ) 
