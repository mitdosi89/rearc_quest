Approach 1 - End to end process completed via aws services only and in python used pandas dataframe for part3 queries

Step 1 : created terraform modules and all .tf files and .py files and attached as .zip package
Step 2 : Everything is working as expected and I will keep resources in my personal aws account for further discussion if given opportunity

Note: Scheduling via event bridge is not done yet so as of now created test event and manually triggering it. 
Also I was facing issues while creating lambda layers via terraform so i created it and use the arn directly in terraform .tf files for both lambdas.
I have attached one lambda layer in mail and other one for pandas I am using ready made available in lambda layers. 

Summary - 

- Created dynamodb tracking table for keeping track of any changes happened in all or single file. 
- SQS queue - used for triggering reporting lambda( part 3 work of quest)
- S3 bucket - having both api data in specific directories and also created s3 event notification to put records in sqs queue
- Two lambdas : First lambda for fetching the data for both files, updating dynamodb tracking table and upload all or single changed file in s3
			  : Second lambda to process queries and its triggered when any record entered in sqs  

Snaps attached along with zip file

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Approach 2 - I worked only on databricks notebook for part3 of quest but thought of mentioning the approach here. Listed set of steps below:

Step 1 : Using ADF(Azure data factory)

a) create linked service - http 
b) create linked service - azure data lake 
c) dynamic datasets and activities like copydata, webactivity, foreach, set variable etc to create pipeline and bring in data from both external locations
and put data in container landing zone in gen2 in storage account
d) schedule the pipeline on daily or hourly basis to check if changes in any file happened or we create two pipelines - one using first three
steps a,b,c to bring one data for one time ingestion and second pipeline for scheduling it to check if any changes happend in files using 
foreach, getmetadata activity etc and  

Note: Due to shortage of time i did not work on step 1

Step 2: Using databricks 

a) Azure Data Lake Storage Gen2 generates events for new file creation, updates, renames, or deletes which are routed via Event Grid and Azure Function to Azure Databricks
b) create staging table and main table via ctas from stg table for csv files and json file. If data is huge we can create partition tables. 
c) any changes happen via step a, will call databricks notebook and will populate staging table first. SCD can be cover here via staging and main table. 
d) when we run workflows(schedule it) and mention dependency as task between notebooks then this main table will be populated from staging table and further 
notebooks for transformations and aggregations will be processed as part of our medallion architecture

Note : As of now for approach 2, due to time limitation, I just work on part 3 queries by simply putting the two files in dbfs system in my databricks community 
edition. 

Few spark optimization technique
 - created tables for csv file and json file and this will not cause one extra unnecessary job for infering schema
 - if require we can create tables(stg and main table) if we have to apply scd and we can use delta as format for main table
 - using delta format for main table ensure 












