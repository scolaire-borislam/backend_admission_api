import json
import logging
import boto3
import botocore
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    #body = json.loads(json.dumps(event['body']))
    
    body = event['body']
    if isinstance(body, str) :
        body = json.loads(body)
    
    
    if 'documentKey' not in body:
        return {
            'statusCode': 400,
            'message': 'input invalid, documentKey is missing'
        }

    if 'actionType' not in body:
        return {
            'statusCode': 400,
            'message': 'input invalid, actionType is missing'
        }

    documentKey = body['documentKey']
    actionType = body['actionType']
    
    # s3_client = boto3.client('s3',region_name="ap-east-1",config=boto3.session.Config(s3={'addressing_style': 'virtual'},signature_version='s3v4'))
    s3_client = boto3.client('s3',endpoint_url="https://s3.ap-southeast-1.amazonaws.com",region_name="ap-southeast-1",config=boto3.session.Config(s3={'addressing_style': 'virtual'},signature_version='s3v4'))

    try:
        if actionType =="put_object" :
            response = s3_client.generate_presigned_url('put_object',
                                                    Params={'Bucket': '2023-project-uwl',
                                                            'Key': documentKey},
                                                    ExpiresIn=600)
        elif actionType =="get_object" :
            response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': '2023-project-uwl',
                                                            'Key': documentKey},
                                                    ExpiresIn=600)
        
        print(response)                                                    
    except Exception as e:
        print(e)
        logging.error(e)
        return "Error"
    
    return {
        'statusCode': 200,
            "headers": {
                'Access-Control-Allow-Headers': '*',                
                'Access-Control-Allow-Methods': '*',
                'Access-Control-Allow-Origin': '*',
                "Access-Control-Max-Age": "0"
            },        
        'body': response
    }