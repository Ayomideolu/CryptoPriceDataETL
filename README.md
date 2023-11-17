# CryptoPriceDataETL
The goal of this project is to generate a summarized table from the crypto price data available on the rapidapi.com.which can be used to predict crypto market price and other form of analysis.

On execution,this program loads all data from the api endpoint,performs data cleansing on the data, writes to s3 bucket for staging and then reads from s3 bucket  in other to transform before loading to the destination database which is  Redshift database,emptying the raw folder in the s3 bucket or moving the content of the raw folder to the processed folder in the s3 bucket in the process.

##Pre-requisite:
In other to run this program you will first need to import all the required libraries from the requirement.txt.
Have a working redhift instance on AWS cloud.
Create a bucket in AWS cloud,create raw_folder,processed_folder,transformed_folder to house the data before loading to redshift.
Use the generate schema table in the util.py to generate a schema in your redshift database.

##Setting up environment:

create an environment variable file that house your database andAPI credentials/secret by running:
 touch.env
pip -r install requirements.txt(install libraries/dependencies)

Your .env file should contain the code below.Replace the value of the variables with your credentials
# API credentials
URL=https://coinranking1.p.rapidapi.com/coins
QUERYSTRING={"referenceCurrencyUuid":"yhjMzLPhuIDl","timePeriod":"24h","tiers[0]":"1","orderBy":"marketCap","orderDirection":"desc","limit":"50","offset":"0"}
HEADERS = {"X-RapidAPI-Key": "c3601b608bmshee59c6a3aa2f0c9p159994jsn5c1383278914","X-RapidAPI-Host": "coinranking1.p.rapidapi.com"}
#Redshift Credentials
IAM_ROLE=your IAM role
USER=your user.
PASSWORD=your redshift password
HOST=your workgroup on aws redshift cluster
DATABASE_NAME=deyour data base name
PORT=your redshift port


##The program needs to run from your main.py module
##The util.py houses all helper function needed for the succesful run of this program.

















