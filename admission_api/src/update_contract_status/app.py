from web3 import Web3
from web3.middleware import geth_poa_middleware
import json
import boto3
import smart_contract_helper
import message_helper

def lambda_handler(event, context):

    try:

        body = event['body']
        if isinstance(body, str) :
            body = json.loads(body)

        if 'app_id' in body:
            app_id = body['app_id']

        if 'status' in body:
            status = body['status']

        if 'check_result' in body:
            check_result = body['check_result']
        else :
            check_result=""


        # tx_hash = smart_contract_helper.update_contract_status(app_id,status)
        msgid = message_helper.send_status_change(app_id,status,check_result)    
        print("Message sent with id:" + msgid)
        
        # print(f"Request send to requirement check smart contract! Transaction hash: {tx_hash}")
        return {
            "statusCode": 200,
            "headers": {
                'Access-Control-Allow-Headers': '*',                
                'Access-Control-Allow-Methods': 'POST',
                'Access-Control-Allow-Origin': '*',
                "Access-Control-Max-Age": "0"
            },
            #"body": json.dumps(response, cls=DecimalEncoder),
            'body': json.dumps({'message': 'SQS message send to status update smart contract function Successfully!'})
        }

    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            "headers": {
                'Access-Control-Allow-Headers': '*',                
                'Access-Control-Allow-Methods': 'POST',
                'Access-Control-Allow-Origin': '*',
                "Access-Control-Max-Age": "0"
            },            
            'body': json.dumps({'error': str(e)})
        }