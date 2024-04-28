import json

# from dynamo import programme_table

import logging

import dynamo
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, Decimal):
      return str(obj)
    return json.JSONEncoder.default(self, obj)

def lambda_handler(event, context):
    """Body optionally expected:
    {
        "lastKey": {
            "id": "2012396d-576d-4dcd-a093-ecc886a75eee",
            "created_dt": "2022-10-21 13:10:11.427197"
        }
    }
    """
    body = event['body']
    if isinstance(body, str) :
        body = json.loads(body)
    
    
    if 'item' not in body:
        return {
            'statusCode': 400,
            'message': 'input invalid'
        }

    item = body['item']

    try:
        print("start update application 1")        
        responseItem = dynamo.update_application(item)
        print("end update application ")
        print(responseItem)

        return {
            "statusCode": 200,
            "headers": {
                'Access-Control-Allow-Headers': '*',                
                'Access-Control-Allow-Methods': 'POST',
                'Access-Control-Allow-Origin': '*',
                "Access-Control-Max-Age": "0"
            },
            #"body": json.dumps(response, cls=DecimalEncoder),
            'body': json.dumps({'message': 'Item added successfully', 'item': responseItem})
        }

    except Exception as e:
        print(e)
        # return {"statusCode": 500, "headers": {}, "body": "Internal Server Error"}
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