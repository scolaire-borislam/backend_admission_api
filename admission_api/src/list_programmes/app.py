import json

# from dynamo import programme_table
# import base64
import logging
# import boto3
# import requests
import dynamo
from decimal import Decimal
# https://www.linkedin.com/pulse/setup-local-dynamodb-docker-nosql-workbench-corinne-roosen/
# https://aws.plainenglish.io/aws-tutorials-build-a-python-crud-api-with-lambda-dynamodb-api-gateway-and-sam-874c209d8af7

# https://github.com/pedrocabido/todo_list_api/blob/master/layers/python/dynamo.py
# https://aws.plainenglish.io/aws-tutorials-build-a-python-crud-api-with-lambda-dynamodb-api-gateway-and-sam-874c209d8af7
# https://medium.com/@christopheradamson253/exploring-aws-lambda-layers-reusing-code-and-dependencies-14a0512bd0ce

# https://medium.com/simform-engineering/creating-lambda-layers-made-easy-with-docker-a-developers-guide-3bcfcf32d7c3
# https://pjdhub.com/2020/11/04/creating-a-lambda-layer/
# https://aws.plainenglish.io/lambda-layer-how-to-create-them-python-version-bc1e027c5fea
# https://pjdhub.com/2020/11/21/lambda-layers-and-local-python-development/

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
        print("1")
        # response = dynamo.test_method()
        response = dynamo.get_all_featured_programmes()
        print("2")
        print(response)

        return {
            "statusCode": 200,
            "headers": {},
            "body": json.dumps(response, cls=DecimalEncoder),

        }

    except Exception as e:
        print(e)
        return {"statusCode": 500, "headers": {}, "body": "Internal Server Error"}