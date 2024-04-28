import json
import boto3

class DecimalEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, Decimal):
      return str(obj)
    return json.JSONEncoder.default(self, obj)

def lambda_handler(event, context):

    try:

        body = event['body']
        if isinstance(body, str) :
            body = json.loads(body)

        if 'username' in body:
            username = body['username']

        if 'password' in body:
            password = body['password']
        ssm = boto3.client('ssm')
        internal_cognito_client_id_parameter = ssm.get_parameter(Name='internal_cognito_client_id', WithDecryption=True)
        internal_cognito_client_id = internal_cognito_client_id_parameter['Parameter']['Value']
        

        client = boto3.client('cognito-idp')
        response = client.initiate_auth(
            
            ClientId= internal_cognito_client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )
        print(response)
        return {
            "statusCode": 200,
            "headers": {
                'Access-Control-Allow-Headers': '*',                
                'Access-Control-Allow-Methods': 'POST',
                'Access-Control-Allow-Origin': '*',
                "Access-Control-Max-Age": "0"
            },
            "body": json.dumps(response, cls=DecimalEncoder),
            # 'body': json.dumps({'message': 'Request send to requirement check smart contract Successfully!'})
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