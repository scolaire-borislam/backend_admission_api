import json
import boto3



def lambda_handler(event, context):

    try:

        
        ssm = boto3.client('ssm')
       
      
        rpc_parameter = ssm.get_parameter(Name='admission_rpcurl', WithDecryption=True)
        rpc_url = rpc_parameter['Parameter']['Value']

        smart_contract_addres_parameter = ssm.get_parameter(Name='admission_contract_address', WithDecryption=True)
        smart_contract_address = smart_contract_addres_parameter['Parameter']['Value']

        external_cognito_pool_id_parameter = ssm.get_parameter(Name='external_cognito_pool_id', WithDecryption=True)
        external_cognito_pool_id = external_cognito_pool_id_parameter['Parameter']['Value']


        external_app_client_secret_parameter = ssm.get_parameter(Name='external_app_client_secret', WithDecryption=True)
        external_app_client_secret = external_app_client_secret_parameter['Parameter']['Value']


        print("start getting ssm parameter ....")
        print(rpc_url)
        print(smart_contract_address)
        print(external_cognito_pool_id)
        print(external_app_client_secret)

        
        



        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                 "Access-Control-Max-Age": "0"
            },
            'body': json.dumps({'rpc_url': rpc_url,
                                'smart_contract_address' : smart_contract_address,
                                'external_app_client_secret' : external_app_client_secret,
                                'external_cognito_pool_id' : external_cognito_pool_id,
                                 })
        }
        
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                 "Access-Control-Max-Age": "0"
            },
            'body': json.dumps({'error': str(e)})
        }