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
    """Body optionally expected:
    {
        "lastKey": {
            "id": "2012396d-576d-4dcd-a093-ecc886a75eee",
            "created_dt": "2022-10-21 13:10:11.427197"
        }
    }
    """
    # print(event)



    try:
        print("start getting programme")
        prog_code = event["queryStringParameters"]['prog_code']
        prog_provider = event["queryStringParameters"]['prog_provider']
        response = dynamo.get_promgramme(prog_code, prog_provider)
        print("End of getting programme")
        print(response)

        return {
            "statusCode": 200,
            "headers": {},
            "body": json.dumps(response, cls=DecimalEncoder),

        }

    except Exception as e:
        print(e)
        return {"statusCode": 500, "headers": {}, "body": "Internal Server Error"}