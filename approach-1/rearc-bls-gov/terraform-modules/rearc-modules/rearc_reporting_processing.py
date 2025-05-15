import json
import io
import pandas as pd
import boto3
import os
from botocore.exceptions import ClientError
import datetime
from boto3.dynamodb.conditions import Key


s3_client = boto3.client('s3')
sqs_queue_url = os.environ['SQS_QUEUE_URL']
sqs_client = boto3.client('sqs')
S3_BUCKET = os.environ['BUCKET_NAME']
dynamodb_tbl = boto3.resource('dynamodb').Table(os.environ['TRACKING_TBL'])

# def getQueueMessage():
#     statusCode = 200
#     response_body = ''
#     try:
#         response = sqs_client.receive_message(
#             QueueUrl=sqs_queue_url,
#             MaxNumberOfMessages=1,
#             WaitTimeSeconds=5
#         )
#         print(response)
#         if 'Messages' in response:
#             response_body = response['Messages'][0]
#     except ClientError as e:
#         print(e)
#         statusCode = 500
#         response_body = 'error getting message'
#     return statusCode, response_body

def deleteQueueMessage(receipt_handle):
    statusCode = 200
    response_body = ''
    try:
        dlt_response = sqs_client.delete_message(
            QueueUrl=sqs_queue_url,
            ReceiptHandle=receipt_handle
        )
        statusCode = dlt_response['ResponseMetadata']['HTTPStatusCode']
        if statusCode == 200:
            print('Message deleted successfully')
            response_body = "message deleted successfully"
    except ClientError as e:
        print(e)
        response_body = 'error deleting message'
    return statusCode, response_body


def pd_read_s3_csv():
    try:
        date_time = datetime.datetime.now().strftime("%m/%d/%Y")
        print('date_time',date_time)
        response = dynamodb_tbl.query(KeyConditionExpression=Key('date_time').eq(date_time))
        if response.get('ResponseMetadata').get('HTTPStatusCode') == 200:
            if response['Items']:
                data = response['Items'][0]
                bls_date_time = data['bls_date_time']
                print(bls_date_time)
        file_name= os.environ['FILE_TO_FETCH']
        key = f"{bls_date_time.replace('/','-')}/{file_name}"
        print(key)
        obj = s3_client.get_object(Bucket=S3_BUCKET, Key=key)
        return pd.read_csv(io.BytesIO(obj['Body'].read()))
    except ClientError as e:
        print(e)
        return pd.DataFrame()

def pd_read_s3_json(bucket_key):
    try:
        key = bucket_key 
        print('key is',key)
        obj = s3_client.get_object(Bucket=S3_BUCKET, Key=key)
        data = json.loads(io.BytesIO(obj['Body'].read()).getvalue().decode('utf8'))['data']
        return pd.DataFrame(data = data,
                            columns=["ID Nation","Nation","ID Year","Year","Population","Slug Nation"]).astype({"ID Nation": str, 
                                        "Nation": str,
                                        "ID Year":int,
                                        "Year": int,
                                        "Population": int,
                                        "Slug Nation": str})
    except ClientError as e:
        print(e)
        return pd.DataFrame()

def calculate_population_mean_std(nation_population_df):
    return nation_population_df[nation_population_df['Year'].isin([2013, 2018])].groupby(['ID Nation'], as_index=False).agg({'Population':['mean', 'std']})

def calculate_series_best_year_max_value(df):
    df.columns=['series_id','year','period','value','footnote_codes']
    df2 = df.groupby(['series_id', 'year'], as_index=False).agg({'value':'sum'})
    df2.columns=['series_id','year','value']
    df3 = df2.sort_values("value", ascending=False).groupby(["series_id"]).first().reset_index()
    return df3

def calculate_series_id_population(nation_population_df, current_data_df):
    first_df = current_data_df.query("period == 'Q01' & series_id.str.strip() == 'PRS30006032'")
    final_result_df = pd.merge(first_df[['series_id','year','period','value']], nation_population_df[['Year','Population']], left_on= 'year',
                    right_on= 'Year', 
                    how = 'inner').drop('Year', axis=1)
    return final_result_df

def lambda_handler(event, context):
    print(event)
    #print(type(event))
    statusCode = 200
    response_body = ''
    bucket_key = json.loads(event['Records'][0]['body'])['Records'][0]['s3']['object']['key']
    #print('bucket_key',bucket_key)
    receiptHandle = event['Records'][0]['receiptHandle']
    #print('receiptHandle', receiptHandle)
    if len(bucket_key) > 0:
        try:
            nation_population_df = pd_read_s3_json(bucket_key)
        
            ### Read Second Data For pr.data.0.Current file
            current_data_df = pd_read_s3_csv()
            #print('current_data_df',current_data_df.head())
            
            ### mean and the standard deviation of the annual US population across the years [2013, 2018] inclusive
            population_mean_std_df = calculate_population_mean_std(nation_population_df)
            print(population_mean_std_df)

            ### best year: the year with the max/largest sum of "value" for all quarters in that year

            series_id_best_year_df = calculate_series_best_year_max_value(current_data_df)
            print(series_id_best_year_df)

            ### value for series_id = PRS30006032 and period = Q01 and the population for that given year 
            
            series_id_population_df = calculate_series_id_population(nation_population_df,current_data_df)
            print(series_id_population_df)

            statusCode, response_body = deleteQueueMessage(receiptHandle)
            if statusCode == 200:
                response_body = 'reporting process successfully completed!'

        except Exception as e:
            print(e)
            statusCode=500
            response_body = 'error in processing report'
    return {
        'statusCode': statusCode,
        'body': response_body
    }
