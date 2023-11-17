
# Import libraries
from time import sleep
from util import generate_schema, execute_sql, transform_data, get_redshift_connection, empty_raw_folder
from etl import get_data_from_api, read_from_s3, write_to_s3, load_to_redshift, read_multi_files_from_s3, \
move_files_to_processed_folder

conn = get_redshift_connection()
# Main method to run the pipeline