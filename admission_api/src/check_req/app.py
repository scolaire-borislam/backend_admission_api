# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Purpose
An AWS lambda function that analyzes documents with Amazon Textract.
"""
import json
import base64
import logging
import boto3
from textractcaller import call_textract, Textract_Features
from textractprettyprinter.t_pretty_print import Pretty_Print_Table_Format, Textract_Pretty_Print, get_string, get_tables_string
from trp import Document
from trp.trp2 import TDocument, TDocumentSchema

from botocore.exceptions import ClientError
import dynamo
import message_helper

# Set up logging.
logger = logging.getLogger(__name__)

# Get the boto3 client.
textract_client = boto3.client('textract')

def isFloat(input):
    try:
        float(input)
    except ValueError:
        return False
    return True

def remove_empty_values(dictionary):
    keys_to_remove = []
    for key, value in dictionary.items():
        if value == '':
            keys_to_remove.append(key)
    for key in keys_to_remove:
        del dictionary[key]

def get_score(subject_grade):
    """
    Maps the subject value to its corresponding score.
    """
    score_mapping = {
        'ABS': 0,
        'UNCL': 0,
        '1(ONE)': 1,
        '2(TWO)': 2,
        '3(THREE)': 3,
        '4(FOUR)': 4,
        '5(FIVE)': 5,
        '5(FIVE*)': 5,
        '5*(FIVE*)': 6,
        '5**(FIVE**)': 7
    }
    # Use partial matching to find the closest match
    for key in score_mapping:
        if key in subject_grade.upper():
            
            # print("subject: " + subject.lower() )
            # print("map - " +  key)
            print(score_mapping[key])
            return score_mapping[key]
    return -1  # Default to 0 if no match is found


def transform_grades(grades):
    result = {}
    for subject, grade in grades.items():
        if '&' in grade:
            # Split the grade into multiple parts
            parts = grade.split('&')
            for i, part in enumerate(parts):
                # Translate each part and add it to the result
                result[subject + '-' + str(i)] = get_score(part)
                # result[f"{subject}{i+1}"] = get_score(part)
        else:
            # Translate the single grade and add it to the result
            result[subject] = get_score(grade)
    return result

def lambda_handler(event, context):
    """
    Lambda handler function
    param: event: The event object for the Lambda function.
    param: context: The context object for the lambda function.
    return: The list of Block objects recognized in the document
    passed in the event object.
    """
    # print(event)
    try:
        # body = json.loads(json.dumps(event['body']))
        body = event['body']
        if isinstance(body, str) :
            body = json.loads(body)
        # print(body)
        print(type(body))
        # Determine document source.

        if 'email' in body:
            email = body['email']

        if 'app_id' in body:
            app_id = body['app_id']


        ssm = boto3.client('ssm')
        bucket_parameter = ssm.get_parameter(Name='admission_bucket', WithDecryption=True)
        bucket_name = bucket_parameter['Parameter']['Value']
        print(bucket_name)
        
        dictHKDSE ={'CHINESE LANGUAGE':'',
                    'ENGLISH LANGUAGE':'',
                    'MATHEMATICS':'',
                    'LIBERAL STUDIES':'',
                    'COMBINED SCIENCE':'',
                    'BIOLOGY':'',
                    'CHEMISTRY':'',
                    'PHYSICS':'',
                    'MUSIC':'',
                    'BUSINESS, ACCOUNTING AND FINANCIAL STUDIES':'',
                    'GEOGRAPHY':'',
                    'INFORMATION AND COMMUNICATION TECHNOLOGY':'',
                    } 
        dicIELTS ={'Listening':'',
                   'Reading':'',
                   'Writing':'',
                   'Speaking':'',
                   'Band':'',}
        cand_response = dynamo.get_cand_application(email,app_id)
        # print(response)
        if cand_response == None :
            raise Exception('No Cand Retrieved')

        docList = []
        if 'education_qualification1' in  cand_response:
            if len(cand_response['education_qualification1']) !=0 :
                doc1 = cand_response['education_qualification1']
                docList.append(doc1)
        if 'education_qualification2' in  cand_response:
            if len(cand_response['education_qualification2']) !=0 :
                doc2 = cand_response['education_qualification2']
                docList.append(doc2)
        if 'education_qualification3' in  cand_response:
            if len(cand_response['education_qualification3']) !=0 :
                doc3 = cand_response['education_qualification3']
                docList.append(doc3)

        pk = cand_response['pk']
        sk = cand_response['sk']

        print(docList)    

        for doc in docList:
            image = {'S3Object':
                     {'Bucket':  bucket_name,
                      'Name': doc}
                     }
            print(image);
            responseDocumentBlock = textract_client.detect_document_text(Document=image)
            hkdse_subject_detected = '' 
            ielts_subject_detected = '' 
            isIELTS = False;
            isHKDSE = False;
            documentTypeChecked=False;
            
            for item in responseDocumentBlock["Blocks"]:
                if item["BlockType"] == "LINE":
                    print ('\033[94m' +  item["Text"] + '\033[0m')

                    if documentTypeChecked == False and "IELTS" in item["Text"]  :
                        print('It is IELTS certificate')
                        isIELTS = True;
                        documentTypeChecked = True;
                
                    if documentTypeChecked == False and "HONG KONG DIPLOMA OF SECONDARY EDUCATION EXAMINATION" in item["Text"]:
                        print('It is HKDSE certificate')
                        isHKDSE = True;  
                        documentTypeChecked = True;  
                    
                    ## It is HKDSE Cert
                    if isHKDSE :                    
                        if hkdse_subject_detected != '':
                            print(hkdse_subject_detected)
                            print(get_score(item["Text"]))
                            if get_score(item["Text"]) > -1:
                                dictHKDSE[hkdse_subject_detected] = item["Text"]
                                hkdse_subject_detected ='' # reset the detected subject to be empty
                                                                

                        if item["Text"] in dictHKDSE:
                            print("HKDSE subject detected") 
                            hkdse_subject_detected = item["Text"]  #next text is the grade
            
                    ## It is IELTS Cert
                    if isIELTS :                  
                        if ielts_subject_detected != '':
                            dicIELTS[ielts_subject_detected] = item["Text"]
                            ielts_subject_detected ='' # reset the detected subject to be empty

                        if item["Text"] in dicIELTS:
                            print("IELTS subject detected") 
                            ielts_subject_detected = item["Text"]  #next text is the grade
                    
        print(dictHKDSE)
        print(dicIELTS)            
            


        # check Eng Requirement
        eng_result_pass = "FAIL"                    
        if 'Band' in  dicIELTS:
            if dicIELTS['Band'] != '':
                ielts_score = float(dicIELTS['Band'] )
                print("ielts score :")
                print(ielts_score)
                if ielts_score > 4.5 :
                    eng_result_pass = "PASS"


        # calculate HKDSE score
        dse_result_pass = "FAIL"
        dse_split_subjects = transform_grades(dictHKDSE)
        print(dse_split_subjects)
        # Calculate the scores for each subject
        best_five_subjects = sorted(dse_split_subjects, key=lambda x: dse_split_subjects[x], reverse=True)[:5]
        print(best_five_subjects)
    
        # Sum the best five subject scores
        dse_sum_of_best_five_subjects = sum([dse_split_subjects[subject] for subject in best_five_subjects if dse_split_subjects[subject] > 0])
        print(dse_sum_of_best_five_subjects)

        print("dse score :")
        print(dse_sum_of_best_five_subjects)
        if dse_sum_of_best_five_subjects > 14:
            dse_result_pass = "PASS"

        # check Chi Requirement
        chi_result_pass = "FAIL"
        if 'CHINESE LANGUAGE' in  dse_split_subjects:
            if dse_split_subjects['CHINESE LANGUAGE'] != '':
                score_chi = dse_split_subjects['CHINESE LANGUAGE']
                print("Chi Grade : " + str(score_chi))
                if score_chi > 2:
                    chi_result_pass = "PASS"

        # check DSE Eng Requirement
        if 'ENGLISH LANGUAGE' in  dse_split_subjects and eng_result_pass != 'PASS':
            if dse_split_subjects['ENGLISH LANGUAGE'] != '':
                score_eng = dse_split_subjects['ENGLISH LANGUAGE']
                print("Eng Grade : " + str(score_eng))
                if score_eng > 2 :
                    eng_result_pass = "PASS"


        # check Math Requirement
        math_result_pass = "FAIL"
        if 'MATHEMATICS' in  dse_split_subjects :
            if 'MATHEMATICS' in  dse_split_subjects and dse_split_subjects['MATHEMATICS'] != ''  :
                score_math = dse_split_subjects['MATHEMATICS']
                print("Math Grade : " + str(score_math))
                if  score_math >2 :
                    math_result_pass = "PASS"

        if 'MATHEMATICS-0' in  dse_split_subjects :
            if dse_split_subjects['MATHEMATICS-0'] != '' and math_result_pass != 'PASS':
                score_math = dse_split_subjects['MATHEMATICS-0']
                print("Math 0 Grade : " + str(score_math))
                if  score_math >2 :
                    math_result_pass = "PASS"

        if 'MATHEMATICS-1' in  dse_split_subjects :
            if dse_split_subjects['MATHEMATICS-1'] != '' and math_result_pass != 'PASS':
                score_math = dse_split_subjects['MATHEMATICS-1']
                print("Math 1 Grade : " + str(score_math))
                if  score_math >2 :
                    math_result_pass = "PASS"

        reponseResult = {
            "chiResult": chi_result_pass,
            "mathResult": math_result_pass,
            "engResult": eng_result_pass,
            "dseResult": dse_result_pass,
            
        }
        app_status='REJECTED-REQ-NOT-MEET'
        if eng_result_pass=='PASS' and \
            math_result_pass=='PASS' and \
              chi_result_pass=='PASS' and \
                dse_result_pass=='PASS' :
            app_status = 'CONDITIONALLY-APPROVED'


        remove_empty_values(dictHKDSE)    
        remove_empty_values(dicIELTS)    

        subject_requirement = "EN-"+eng_result_pass +"#" \
                                "MA-"+math_result_pass +"#" \
                                "DS-"+dse_result_pass \

        # check if app status is the same before send sqs and update ddb
        item = dynamo.get_cand_application(email,app_id)
        originalStatus = item["status"]

        print("original Status : " + originalStatus)
        print("proposed new atatus : " + app_status )

        if originalStatus.strip()  != app_status.strip()  :
            print("Status different start update")
            # update requirement check result to DDB table
            updatecand ={
                "pk": pk,
                "sk": sk,
                "dse_result" : dictHKDSE,
                "ielts_result" : dicIELTS,
                "requirement_check_result" : reponseResult,
                "status" : app_status
            }
            updated_response = dynamo.update_application(updatecand)
            print(updated_response)

            # send sqs to start update contract status in blockchain
            msgid = message_helper.send_status_change(app_id,app_status,subject_requirement)    
            print("Message sent with id:" + msgid)
            # tx_hash = smart_contract_helper.update_contract_status(app_id,app_status)
        
        
        # print(f"Request send to smart contract! Transaction hash: {tx_hash}")
        


                                
        # response_string = app_id + '#' + app_status  + '#' +subject_requirement
        response_string =  subject_requirement
        
        response_dict = {"result" : response_string}
        
        lambda_response = {
            "statusCode": 200,
            'headers': {
                'Access-Control-Allow-Headers': '*',                
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
                'Access-Control-Allow-Origin': '*',
                "Access-Control-Max-Age": "0"
            },            
            "body": json.dumps(response_dict)
        }
        print(lambda_response)
    except ClientError as err:
        error_message = "Couldn't analyze image. " + \
            err.response['Error']['Message']

        lambda_response = {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Headers': '*',                
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
                'Access-Control-Allow-Origin': '*',
                "Access-Control-Max-Age": "0"
            },            
            'body': {
                "Error": err.response['Error']['Code'],
                "ErrorMessage": error_message
            }
        }
        logger.error("Error function %s: %s",
            context.invoked_function_arn, error_message)

    except ValueError as val_error:
        lambda_response = {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Headers': '*',                
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
                'Access-Control-Allow-Origin': '*',
                "Access-Control-Max-Age": "0"
            },
            'body': {
                "Error": "ValueError",
                "ErrorMessage": format(val_error)
            }
        }
        logger.error("Error function %s: %s",
            context.invoked_function_arn, format(val_error))

    return lambda_response
