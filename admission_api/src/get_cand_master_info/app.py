import json

import logging

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
        pk = event["queryStringParameters"]['pk']
        print(pk)
        response = dynamo.get_cand_master_info(pk)
        
        # print(response)
        print("End : get cand master info")
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                 "Access-Control-Max-Age": "0"
            },
            "body": json.dumps(response, cls=DecimalEncoder),

        }

    except Exception as e:
        print(e)
        return {"statusCode": 500, 
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                 "Access-Control-Max-Age": "0"
            },
                "body": "Internal Server Error"}