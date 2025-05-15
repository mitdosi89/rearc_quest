import json
import requests
import os
import boto3
import re
from bs4 import BeautifulSoup
from datetime import datetime
import time
from boto3.dynamodb.conditions import Key
import pandas as pd
import io,base64
from io import StringIO
import pandas as pd

dynamodb_tbl = boto3.resource('dynamodb').Table(os.environ['TRACKING_TBL'])
s3 = boto3.client('s3')

headers = {
            'User-Agent': os.environ['USER_AGENT'],
            'Content-type': os.environ['CONTENT_TYPE']
        }

def process_record_tracking_tbl(date_time,bls_date_time,process_type,final_json_result_dict):
    record_items={}
    try:
        if process_type == 'insert':
            record_items['date_time'] = date_time
            record_items['bls_date_time'] = bls_date_time
            record_items['files_details'] = json.dumps(final_json_result_dict[date_time])
            response = dynamodb_tbl.put_item(
                Item = record_items
            )
        elif process_type == 'update':
            record_items['files_details'] = json.dumps(final_json_result_dict[date_time])
            response = dynamodb_tbl.update_item(
                Key = {
                    'date_time': date_time
                },
                UpdateExpression = "set files_details=:files_details, bls_date_time=:bls_date_time",
                ExpressionAttributeValues = {
                    ':files_details': json.dumps(final_json_result_dict[date_time]),
                    ':bls_date_time': bls_date_time
                },
                ReturnValues = "UPDATED_NEW"
            )
        else:
            response = dynamodb_tbl.query(KeyConditionExpression=Key('date_time').eq(date_time))
    except Exception as e:
        print(e)
        print(response)
    print('response is', response)
    return response

# def fetch_record_details_tracking_tbl(date_time,final_json_result_dict):
#     try:
#         table_name = "v2-integration-rearc-tracking-tbl"
#         response = dynamodb_tbl.query(KeyConditionExpression=Key('date_time').eq(date_time))
#         data = response['Items'][0]
#     except Exception as e:
#         print(e)
#     return data

def fetch_api_data():
    try:
        url = os.environ['NATION_POPULATION_API_URL']
        response = requests.get(url, headers=headers)
        print(response.json())
        response = s3.put_object(
            Body=json.dumps(response.json()),
            Bucket=os.environ['BUCKET_NAME'],
            Key=os.environ['KEY_NATION_POPULATION_DATA']
        )
    except Exception as e:
        print(e)
    return response

def find_all_matches(pattern, string, group=0):
    pat = re.compile(pattern)
    pos = 0
    out = []
    while m := pat.search(string, pos):
        pos = m.start() + 1
        out.append(m[group])
    return out

def getrearcdata(rearc_url):
    final_json_result_dict={}
    pat = r'(?<=\<br/>).+?(?=\</a>)'
    regex_pat = r'(\d+\/\d+\/\d+)(.*?)(\d+:\d+\s+AM|PM)(.*?)(href="(.*?)">)'
    all_files_details=[]
    statusCode = 200
    response_body = ''
    try:
        response = requests.get(rearc_url,headers=headers)
        print(json.loads(json.dumps(response.text)))
        result = find_all_matches(pat, str(BeautifulSoup(json.loads(json.dumps(response.text)), "html.parser").find('pre')))
        for i in result:
            result_json_dict={}
            regex_res = re.findall(regex_pat,i)
            in_time = datetime.strptime(regex_res[0][2], "%I:%M %p")
            out_time = datetime.strftime(in_time, "%H:%M")
            final_date_time = regex_res[0][0]+ " "+ out_time
            date_struct = time.strptime(final_date_time, '%m/%d/%Y %H:%M')
            epoch_time = time.mktime(date_struct)
            file_with_url = os.environ['REARC_URL'] + regex_res[0][6].split('/')[-1]
            result_json_dict['file_name_with_path'] = file_with_url
            result_json_dict['file_last_updated'] = epoch_time
            result_json_dict['file_size'] = re.findall(r'\d+',regex_res[0][4])[0]
            all_files_details.append(result_json_dict)
            print(all_files_details)
            bls_date_time = regex_res[0][0]
        date_time = datetime.now().strftime("%m/%d/%Y")
        print('date_time is',date_time)
        print('bls_date_time is', bls_date_time)
        all_files_details = [dict(t) for t in {tuple(d.items()) for d in all_files_details}]
        final_json_result_dict[date_time] = all_files_details
        print(final_json_result_dict)
        statusCode,response_body = checkFiles(date_time,bls_date_time,final_json_result_dict)
    except Exception as e:
        print(e)
        statusCode = 404
        response_body = {'body':'error fetching bls gov data'}
    return statusCode,response_body

def process_and_upload_files(date_time,files_list):
    statusCode = 200
    response_body = ''
    try:
        bucket_name = os.environ['BUCKET_NAME']
        for file in files_list:
            file_name = file.get('file_name_with_path')
            response = requests.get(file_name,headers=headers)
            decode_content = response.content.decode('utf-8')
            StringData = StringIO(decode_content)
            df = pd.read_csv(StringData, sep='\t', header='infer')
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False,header=True,sep=',')
            csv_buffer.seek(0)
            #bucket_name_with_prefix = date_time.replace("/","-") + "/" + file_name.split('/')[-1] + '.parquet'
            bucket_name_with_prefix = date_time.replace("/","-") + "/" + file_name.split('/')[-1] + '.csv'
            response = s3.put_object(Bucket=bucket_name, Body=csv_buffer.getvalue(),Key=bucket_name_with_prefix)
        response_body = {'body': 'files uploaded successfully'}
    except Exception as e:
        print(e)
        statusCode = 404
        response_body = {'body': 'error uploading files to s3'}
    return statusCode, response_body


def checkFiles(date_time,bls_date_time,final_json_result_dict):
    changed_files = []
    bls_date_time_flag = False
    try:
        response = process_record_tracking_tbl(date_time,bls_date_time,'fetch',final_json_result_dict)
        if response.get('ResponseMetadata').get('HTTPStatusCode') == 200:
            if response['Items']:
                data = response['Items'][0]
                fetch_date_time = data['date_time']
                fetch_bls_date_time = data['bls_date_time']
                fetch_values = json.loads(data['files_details'])
                if date_time == data.get('date_time'):
                    print('date_time matched')
                    if fetch_bls_date_time == bls_date_time: 
                        print('bls_date_time matched')
                        for i in final_json_result_dict[date_time]:
                            if i not in fetch_values:
                                changed_files.append(i)
                    if fetch_bls_date_time != bls_date_time:
                        for i in final_json_result_dict[date_time]:
                            if i not in fetch_values:
                                changed_files.append(i)
                        if not changed_files:
                            bls_date_time_flag=True
                else:
                    response = process_record_tracking_tbl(date_time,bls_date_time,'insert',final_json_result_dict)    
                    if response.get('ResponseMetadata').get('HTTPStatusCode') == 200:
                        statusCode = 200
                        response_body = {'body': 'bls gov data inserted successfully in tracking table'}
                        ### process files in s3 in respective datetime directory
                        statusCode,response_body = process_and_upload_files(bls_date_time,final_json_result_dict.get(date_time))    
                if changed_files:
                    print('changed_files', changed_files)
                    response = process_record_tracking_tbl(date_time,bls_date_time,'update',final_json_result_dict)
                    if response.get('ResponseMetadata').get('HTTPStatusCode') == 200:
                        statusCode = 200
                        response_body = {'body': 'bls gov data updated successfully in tracking table'}
                        ### process files in s3 in respective datetime directory
                        statusCode,response_body = process_and_upload_files(bls_date_time,changed_files)    
                else:
                    if bls_date_time_flag:
                        response = process_record_tracking_tbl(date_time, bls_date_time, 'update', final_json_result_dict)
                        if response.get('ResponseMetadata').get('HTTPStatusCode') == 200:
                            statusCode = 200
                            response_body = {'body': 'bls date time updated successfully in tracking table but no changes in files'}
                    else:
                        statusCode = 200
                        response_body = {'body': 'no changes in bls gov data'}
            else:
                response = process_record_tracking_tbl(date_time,bls_date_time, 'insert', final_json_result_dict)
                if response.get('ResponseMetadata').get('HTTPStatusCode') == 200:
                    statusCode = 200
                    response_body = {'body': 'bls gov data inserted successfully in tracking table'}
                    ### process files in s3 in respective datetime directory
                    statusCode,response_body = process_and_upload_files(bls_date_time, final_json_result_dict.get(date_time))        
    except Exception as e:
        print(e)
        statusCode = 404
        response_body = {'body': 'error fetching bls gov data'}
    return statusCode, response_body

def lambda_handler(event, context):
    statusCode = 200
    response_body = ''
    try:
        rearc_url = os.environ['REARC_URL']  
        statusCode,response_body = getrearcdata(rearc_url)
        response = fetch_api_data()
        print(response)
    except Exception as e:
        print(e)

    return {
        'statusCode': statusCode,
        'body': response_body
    }
