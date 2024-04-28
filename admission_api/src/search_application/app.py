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
        print("Start : search application")

        # if  event["queryStringParameters"] :
        param = event["queryStringParameters"]
        email = ""
        app_no = ""
        prog_code = "" 

        if param:
            if 'email' in param:
                email = param['email']
            else :
                email = ""

            if 'app_no' in param:
                app_no = param['app_no']
            else :
                app_no = ""

            if 'prog_code' in param:
                prog_code = param['prog_code']
            else :
                prog_code = ""

        
        print("print input parameter")
        print("email : ",email)
        print("app_no : " + app_no)
        print("prog_code : " + prog_code)
        print(5)
        response = dynamo.search_appliaction_list(email,app_no, prog_code)
        
        print(response)
        print("End : search application")
        return {
            "statusCode": 200,
            "headers": {
                'Access-Control-Allow-Headers': '*',                
                'Access-Control-Allow-Methods': 'POST',
                'Access-Control-Allow-Origin': '*',
                "Access-Control-Max-Age": "0"
            },
            "body": json.dumps(response, cls=DecimalEncoder),

        }

    except Exception as e:
        print(e)
        return {"statusCode": 500, 
                "headers": {
                    'Access-Control-Allow-Headers': '*',                
                    'Access-Control-Allow-Methods': 'POST',
                    'Access-Control-Allow-Origin': '*',
                    "Access-Control-Max-Age": "0"
                }, 
                "body": "Internal Server Error"}