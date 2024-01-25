from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from util import read_multi_files_from_s3, write_to_s3, generate_schema, execute_sql, get_redshift_connection, empty_raw_folder, move_files_to_processed_folder
from etl import get_data_from_api, transform_data, load_to_redshift
# Define default_args to set the start date, schedule interval, and other parameters
default_args = {
    'owner': 'Ayomide',
    'start_date': datetime(2023, 8, 23),
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

# Define DAG with a unique ID, default_args, and a schedule interval
dag = DAG(
    'crypto_price_data_etl',
    default_args=default_args,
    description='ETL pipeline for crypto price data',
    schedule_interval=timedelta(days=1),  # Run the DAG daily
)

# Define Python operators for each ETL step
def pull_data_from_api():
    crypto_price_data = get_data_from_api()
    write_to_s3(crypto_price_data, 'ayomide-crypto-price-data', 'raw_data')

def transform_data_in_s3():
    raw_data = read_multi_files_from_s3('ayomide-crypto-price-data', 'raw_data')
    transformed_data = transform_data(raw_data)
    write_to_s3(transformed_data, 'ayomide-crypto-price-data', 'transformed_data')

def load_to_redshift_table(transformed_data):
    conn = get_redshift_connection()
    create_table_query = generate_schema(transformed_data, 'crypto_price_data')
    execute_sql(create_table_query, conn)
    load_to_redshift('ayomide-crypto-price-data', 'transformed_data', 'crypto_price_data')

def clean_up_raw_data():
    move_files_to_processed_folder('ayomide-crypto-price-data', 'raw_data', 'processed_data')
    
    

# Define tasks using PythonOperators
pull_data_task = PythonOperator(
    task_id='pull_data_from_api',
    python_callable=pull_data_from_api,
    dag=dag,
)

transform_data_task = PythonOperator(
    task_id='transform_data_in_s3',
    python_callable=transform_data_in_s3,
    dag=dag,
)

load_to_redshift_task = PythonOperator(
    task_id='load_to_redshift_table',
    python_callable=load_to_redshift_table,
    dag=dag,
)

clean_up_raw_data_task = PythonOperator(
    task_id='clean_up_raw_data',
    python_callable=clean_up_raw_data,
    dag=dag,
)

# Set task dependencies
pull_data_task >> transform_data_task >> load_to_redshift_task >> clean_up_raw_data_task




