import boto3
import psycopg2
import pandas as pd
from io import StringIO
import io
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

def generate_schema(data, table_name):
    create_table_statement = f'CREATE TABLE IF NOT EXISTS {table_name}(\n'
    column_type_query = ''
    
    types_checker = {
        'INT':pd.api.types.is_integer_dtype,
        'VARCHAR':pd.api.types.is_string_dtype,
        'FLOAT':pd.api.types.is_float_dtype,
        'TIMESTAMP':pd.api.types.is_datetime64_any_dtype,
        'BOOLEAN':pd.api.types.is_bool_dtype,
        'ARRAY':pd.api.types.is_list_like,
    }
    for column in data: # Iterate through all the columns in the dataframe
        last_column = list(data.columns)[-1] # Get the name of the last column
        for type_ in types_checker:
            mapped = False
            if types_checker[type_](data[column]):
                mapped = True
                if column != last_column:
                    column_type_query += f'{column} {type_},\n'
                else:
                    column_type_query += f'{column} {type_}\n'
                break
        if not mapped:
            raise ('Type not found')
    column_type_query += ');'
    output_query = create_table_statement + column_type_query
    return output_query


def execute_sql(sql_query, conn):
    conn = get_redshift_connection()
    cur = conn.cursor()
    cur.execute(sql_query)
    conn.commit()
    cur.close() # Close cursor
    conn.close() # Close connection


def list_files_in_folder(bucket_name, folder):
    bucket_list = s3_client.list_objects(Bucket = bucket_name, Prefix = folder) # List the objects in the bucket
    bucket_content_list = bucket_list.get('Contents')
    files_list = [file.get('Key') for file in bucket_content_list][1:]
    return files_list


def move_files_to_processed_folder(bucket_name, raw_data_folder, processed_data_folder):
    file_paths = list_files_in_folder(bucket_name, raw_data_folder)
    for file_path in file_paths:
        file_name = file_path.split('/')[-1]
        copy_source = {'Bucket': bucket_name, 'Key': file_path}
        # Copy files to processed folder
        s3_resource.meta.client.copy(copy_source, bucket_name, processed_data_folder + '/' + file_name)
        s3_resource.Object(bucket_name, file_path).delete()
    print("Files successfully moved to 'processed_data' folder in S3")


def empty_raw_folder(bucket_name, raw_data_folder):
    file_paths = list_files_in_folder(bucket_name, raw_data_folder)
    for file_path in file_paths:
        s3_resource.Object(bucket_name, file_path).delete()
    print("Files deleted from raw data folder")
