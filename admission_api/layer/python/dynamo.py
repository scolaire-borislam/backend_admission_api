import os
# import logging
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
import datetime

# logger = logging.getLogger(__name__)


def generate_timestamp():
    now = datetime.datetime.now()
    formatted_timestamp = now.strftime("%Y%m%d-%H%M%S")
    return formatted_timestamp


def generate_appno(prog_code):
    now = datetime.datetime.now()
    formatted_timestamp = now.strftime("%Y%m%d%H%M%S")
    return prog_code + '-' +formatted_timestamp

def programme_table():
    print("start getting programme table");
    table_name = os.environ.get("TABLE", "programme")
    region = os.environ.get("REGION", "ap-southeast-1")
    aws_environment = os.environ.get("AWSENV","AWS_SAM_LOCAL") # not work and not needed if connected to cloud
    #aws_environment = os.environ["AWSENV"]
    print("i-1");
    print(aws_environment);
    print("i-2");

    print("i-3");

    
    actions_table = boto3.resource("dynamodb",  region_name=region)
    print("end getting programme table");
    return actions_table.Table(table_name)




def cand_application_table():
    print("start getting cand_application table");
    table_name = os.environ.get("TABLE", "cand_application")
    region = os.environ.get("REGION", "ap-southeast-1")
    aws_environment = os.environ.get("AWSENV","AWS_SAM_LOCAL") # not work and not needed if connected to cloud
    print(aws_environment);
    actions_table = boto3.resource("dynamodb",  region_name=region)
    print("end getting application table");
    return actions_table.Table(table_name)

def update_application(item ) :
    app_table = cand_application_table() 
    appl_timestamp = generate_timestamp()
    item["last_update_time"] = appl_timestamp
    
    # Check if 'PK' and 'SK' are present in the item
    if 'pk' in item and 'sk' in item:

        print('start update item')
        # Construct the UpdateExpression dynamically
        update_expression = "SET "
        expression_attribute_values = {}
        for attr_name, attr_value in item.items():
            if attr_name not in ['pk', 'sk']:
                update_expression += f"#{attr_name} = :{attr_name}, "
                expression_attribute_values[f":{attr_name}"] = attr_value

        # Remove trailing comma and space
        update_expression = update_expression.rstrip(", ")
        print(update_expression)
        print(item['pk'])
        print(item['sk'] )
        
        print(expression_attribute_values)
        # Execute the update
        response = app_table.update_item(
            Key={
                'pk': item['pk']  ,
                'sk': item['sk'] 
            },
            UpdateExpression=update_expression,
            ExpressionAttributeNames={f"#{attr}": attr for attr in item.keys() if attr not in ['pk', 'sk']},
            ExpressionAttributeValues=expression_attribute_values
        )
        print(f"Item updated: {response}")
        return item
    else:
        # Call put_item
        print('start put item....')


        # app_no = f"{item.get('prog_code')}-{appl_timestamp}"

        app_no =generate_appno(item.get('prog_code'))

        item['sk'] = app_no 
        item["create_date"] = appl_timestamp
        print( item)
        response = app_table.put_item(Item=item)
        print(f"Item added: {response}")
        return item
    #return response

def get_appliaction_list(email) :

    try:
        # Specify the partition key value
        partition_key_value = email

        print('start get application list ...')

        #table = application_table() 
        table = cand_application_table()
        query_params = {
            'IndexName': 'GSI_EMAIL_ID',            
            'KeyConditionExpression': '#partition_key = :partition_value ',
            'ExpressionAttributeNames': {
                '#partition_key': 'email',
            },
            'FilterExpression': 'sk <> :cand',
            'ExpressionAttributeValues': {
                ':partition_value': partition_key_value,
                ':cand': 'CAND',
            },
            'ScanIndexForward': False  # Set to True for ascending order
        }      
        response = table.query(**query_params)

        print("end of query application");
    except ClientError as err:
        print(err)
        # logger.error(
        #     "Couldn't query for programme released. Here's why: %s: %s",            
        #     err.response["Error"]["Code"],
        #     err.response["Error"]["Message"],
        # )
        raise
    else:
        return response["Items"]


def get_cand_master_info(pk) :

    try:

        print('start get cand master info  ...')

        table = cand_application_table() 
        response = table.query(          
            KeyConditionExpression='pk = :value1 AND sk = :value2',
            ExpressionAttributeValues={
                ':value1': pk,
                ':value2': 'CAND'
            }

        )
        print(response);
        if len(response['Items']) > 0:
            # Process the retrieved item (e.g., print or return it)
            item = response['Items'][0]
            print(f"Retrieved item: {item}")
            print("end of cand master  info");
            return item
        else:
            print("Item not found.")
            print("end of query cand master info");
            return None    
        
    except Exception as e:
        print(f"Error querying DynamoDB: {e}")
        raise


def get_cand_application(email, app_id) :

    try:

        print('start get application  ...')

        table = cand_application_table() 
        response = table.query(
            IndexName='GSI_EMAIL_APP_ID',            
            KeyConditionExpression='email = :value1 AND sk = :value2',
            ExpressionAttributeValues={
                ':value1': email,
                ':value2': app_id
            }

        )
        print(response);
        if len(response['Items']) > 0:
            # Process the retrieved item (e.g., print or return it)
            item = response['Items'][0]
            print(f"Retrieved item: {item}")
            print("end of query application");
            return item
        else:
            print("Item not found.")
            print("end of query application");
            return None    
        # response = table.get_item(
        #         Key={
        #             'pk': pk,
        #             'sk': sk
        #         }
        #     )
        # item = response.get('Item')
        # if item:
        #     # Process the retrieved item (e.g., print or return it)
        #     print(f"Retrieved item: {item}")
        #     print("end of query application");
        #     return item
        # else:
        #     print("Item not found.")
        #     print("end of query application");
        #     return None
        
    except Exception as e:
        print(f"Error querying DynamoDB: {e}")
        raise
        


def get_promgramme(prog_code, prog_provider) :
    try:
        print('start get programme  ...')

        table = programme_table()
        response = table.get_item(
                Key={
                    'prog_code': prog_code,
                    'prog_provider': prog_provider
                }
            )
        item = response.get('Item')
        if item:
            # Process the retrieved item (e.g., print or return it)
            print(f"Retrieved item: {item}")
            print("end of query programme");
            return item
        else:
            print("Item not found.")
            print("end of query programme");
            return None
    except Exception as e:
        print(f"Error querying DynamoDB: {e}")
        raise


def get_all_featured_programmes():
    try:
        print("start get featured programmes ...");
        table = programme_table()
        print("01");
        
        response = table.query(
            IndexName='GSI_FEATURED_PCODE',
            KeyConditionExpression=Key('featured').eq('Y') & Key('prog_code').begins_with('UWL')
        )
        print("02");
    except ClientError as err:
        print(err)
        # logger.error(
        #     "Couldn't query for programme released. Here's why: %s: %s",            
        #     err.response["Error"]["Code"],
        #     err.response["Error"]["Message"],
        # )
        raise
    else:
        return response["Items"]


def search_appliaction_list(email, app_no, prog_code) :

    try:
        expression_attribute_values= {}

        filterExpressionStr = 'sk <> :cand '
        expression_attribute_values[':cand'] = 'CAND'

        if email != "":
            filterExpressionStr += " AND email = :email"
            expression_attribute_values[':email'] = email

        if app_no != "":
            filterExpressionStr += " AND sk = :app_no"
            expression_attribute_values[':app_no'] = app_no

        if prog_code != "":
            filterExpressionStr += " AND prog_code = :prog_code"
            expression_attribute_values[':prog_code'] = prog_code    

        print(filterExpressionStr)
        print(expression_attribute_values)
        # Specify the partition key value
        table = cand_application_table() 
        print('search  application list ...')


        query_params = {
            'FilterExpression': filterExpressionStr ,
            'ExpressionAttributeValues': expression_attribute_values,
        }  

        response = table.scan(** query_params)

        print(response)
        print(len(response["Items"]))


        print("end of query application");
        
    except ClientError as err:
        print(err)
        raise
    else:
        return response["Items"]
    
