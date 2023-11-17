import boto3
import psycopg2
import pandas as pd
from datetime import datetime
from dotenv import dotenv_values
dotenv_values()

# Get credentials from environment variable file
config = dotenv_values('.env')

# Create a boto3 s3 client and resource for bucket operations
s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')

# function to get Reshift data warehouse connection
def get_redshift_connection():
    user = config.get('USER')
    password = config.get('PASSWORD')
    host = config.get('HOST')
    database_name = config.get('DATABASE_NAME')
    port = config.get('PORT')
    conn = psycopg2.connect(f'postgresql://{user}:{password}@{host}:{port}/{database_name}')
    return conn
