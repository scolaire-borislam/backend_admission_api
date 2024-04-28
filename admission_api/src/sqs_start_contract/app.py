import json
import boto3
import smart_contract_helper

def lambda_handler(event, context):
    print('start trigger')
    # SQS client
    sqs = boto3.client('sqs')

    # Queue URL 
    queue_url = 'https://sqs.ap-southeast-1.amazonaws.com/885596329441/scolaire-contract-queue'
    
    receipt_handle = None
    try:
        
        for record in event['Records']:
            message = record['body']

            if isinstance(message, str) :
                message = json.loads(message)

            if 'message_type' in message:
                message_type = message['message_type']
                print(message_type)

            if message_type == "STATUS_CHANGE" :
                
                if 'app_id' in message:
                    app_id = message['app_id']
                    print(app_id)

                if 'status' in message:
                    status = message['status']
                    print(status)

                if "check_result" in message:
                    check_result = message['check_result']
                    print(check_result)

                print(f"Received message from sqs: {message}")

                tx_hash = smart_contract_helper.update_contract_status(app_id,status,check_result)
                        
                print(f"Request send to smart contract status update! Transaction hash: {tx_hash}")



            if message_type == "REQ_CHECK" :

                if 'app_id' in message:
                    app_id = message['app_id']
                    print(app_id)

                if 'email' in message:
                    email = message['email']
                    print(email)
                print(f"Received message from sqs: {message}")

                tx_hash = smart_contract_helper.req_check(email, app_id)

                print(f"Request send to requirement check smart contract! Transaction hash: {tx_hash}")


            # Get SQS receipt handle
            receipt_handle = record['receiptHandle']
    except Exception as e:
        print(e)
        raise 

    finally:

        try:
          # Delete message in finally 
          sqs.delete_message(
              QueueUrl=queue_url,
              ReceiptHandle=receipt_handle
          )  
          print("message deleted successfully! " + receipt_handle)
        except Exception as e:
          print(f"Error deleting message: {e}")
