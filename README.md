# CryptoPriceDataETL Project
## Overview
The CryptoPriceDataETL project aims to gather and transform cryptocurrency price data from the rapidapi.com endpoint, creating a summarized table for predictive analysis and market insights. The data undergoes a series of steps, including extraction, cleansing, staging in an S3 bucket, transformation, and final loading into a Redshift database. The process ensures data integrity and efficiency in handling crypto market information.

## Project Execution
Upon execution, the program retrieves data from the rapidapi.com endpoint, performs necessary data cleansing, and writes the data into an S3 bucket for staging. Subsequently, the program reads the staged data from the S3 bucket, transforms it by adding date and price columns, and loads it into the destination Redshift database. To maintain organization, the program either empties the raw folder in the S3 bucket or moves its content to the processed folder during the process.

## Prerequisites
Before running the program, ensure you have the required libraries installed using the command: pip install -r requirements.txt. Additionally, set up a working Redshift instance on AWS, create an AWS bucket with raw, processed, and transformed folders, and generate a schema table in your Redshift database using the generate_schema_table function in util.py.

## Setting up Environment
Create an environment variable file by running: touch .env
Install the required libraries using: pip install -r requirements.txt
Populate your .env file with the necessary credentials. Replace the placeholder values with your actual credentials for the API and Redshift database.


## API credentials
URL=https://coinranking1.p.rapidapi.com/coins
QUERYSTRING={"referenceCurrencyUuid":"yhjMzLPhuIDl","timePeriod":"24h","tiers[0]":"1","orderBy":"marketCap","orderDirection":"desc","limit":"50","offset":"0"}
HEADERS = {"X-RapidAPI-Key": "your_api_key_here","X-RapidAPI-Host": "coinranking1.p.rapidapi.com"}

## Redshift Credentials
IAM_ROLE=your IAM role
USER=your user
PASSWORD=your Redshift password
HOST=your workgroup on AWS Redshift cluster
DATABASE_NAME=your database name
PORT=your Redshift port
## Running the Program
Execute the program from your main.py module, utilizing the helper functions housed in util.py for a successful run.
















