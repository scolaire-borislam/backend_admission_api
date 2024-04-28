import json

# from dynamo import programme_table
# import base64
import logging
# import boto3
# import requests
import dynamo
from decimal import Decimal


class DecimalEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, Decimal):
      return str(obj)
    return json.JSONEncoder.default(self, obj)

def lambda_handler(event, context):
 

    try:
        print("Start : get cand application")
        email = event["queryStringParameters"]['email']
        app_id = event["queryStringParameters"]['app_id']
        print(app_id)
        print(email)
        response = dynamo.get_cand_application(email,app_id)
        
        # print(response)
        print("End : get application")
        return {
            "statusCode": 200,
            "headers": {},
            "body": json.dumps(response, cls=DecimalEncoder),

        }

    except Exception as e:
        print(e)
        return {"statusCode": 500, "headers": {}, 
                "body": "Internal Server Error"}