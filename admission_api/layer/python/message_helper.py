import boto3
import json

def send_status_change(app_id , status, check_result):
    print("start send_status_change")
    # SQS client
    sqs = boto3.client('sqs')

    # Queue URL 
    queue_url = 'https://sqs.ap-southeast-1.amazonaws.com/885596329441/scolaire-contract-queue'

    # Message data
    message_body = {'app_id': app_id, 'status': status,"check_result": check_result ,'message_type' : "STATUS_CHANGE"} 
    print(message_body)
    # Send message
    response = sqs.send_message(
        QueueUrl=queue_url,
        DelaySeconds=0,
        MessageBody=(json.dumps(message_body))  
    )

    print(response['MessageId'])
    return response['MessageId']



def send_requirement_check(email , app_id):
    print("start send_requirement_check")
    # SQS client
    sqs = boto3.client('sqs')

    # Queue URL 
    queue_url = 'https://sqs.ap-southeast-1.amazonaws.com/885596329441/scolaire-contract-queue'

    # Message data
    message_body = {'email': email, 'app_id': app_id, 'message_type' : "REQ_CHECK"} 
    print(message_body)
    # Send message
    response = sqs.send_message(
        QueueUrl=queue_url,
        DelaySeconds=0,
        MessageBody=(json.dumps(message_body))  
    )

    print(response['MessageId'])
    return response['MessageId']