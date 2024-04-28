import json
import boto3
from PIL import Image, ImageDraw,ImageFont
from io import BytesIO
import logging

import dynamo
from decimal import Decimal
from web3 import Web3
from web3.middleware import geth_poa_middleware
import smart_contract_helper
import message_helper
import dynamo
class DecimalEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, Decimal):
      return str(obj)
    return json.JSONEncoder.default(self, obj)


def lambda_handler(event, context):

    try:

        print("start issue card")
        body = event['body']
        if isinstance(body, str) :
            body = json.loads(body)

        if 'to_addr' not in body:
            return {
            'statusCode': 400,
            'message': 'input invalid, To addres is missing'
            }


        if 'email' not in body:
            return {
            'statusCode': 400,
            'message': 'input invalid, candidate email is missing'
            }

        if 'uid' not in body:
            return {
            'statusCode': 400,
            'message': 'input invalid, candidate uid is missing'
            }

        if 'app_no' not in body:
            return {
            'statusCode': 400,
            'message': 'input invalid, candidate App No is missing'
            }

        if 'institution' not in body:
            return {
            'statusCode': 400,
            'message': 'input invalid, institution code No is missing'
            }




        print("getting parameter for issue card")
        to_wallet_address = body['to_addr']
        # token_metadata = body['metadata']
        uid = body['uid']
        app_no = body['app_no']
        email = body['email']
        institution = body['institution']
        # to_wallet_address = event["queryStringParameters"]['to_addr']
        # token_metadata = event["queryStringParameters"]['metadata']



        if institution != 'UWL' and institution != 'HKIT':
            raise Exception("Institution code not found")


        candApp = dynamo.get_cand_application(email,app_no)
        surname = candApp["surname"]
        given_name = candApp["given_name"]
        photo_path = candApp["photo_path"]
        mode_of_study =candApp["mode_of_study"]

        
        ssm = boto3.client('ssm')
       
        private_bucket_parameter = ssm.get_parameter(Name='admission_bucket', WithDecryption=True)
        private_bucket_name = private_bucket_parameter['Parameter']['Value']

        public_bucket_parameter = ssm.get_parameter(Name='admission_bucket_public', WithDecryption=True)
        public_bucket_name = public_bucket_parameter['Parameter']['Value']
        token_image_parameter = ssm.get_parameter(Name='admission_token_image_url', WithDecryption=True)
        token_image_url = token_image_parameter['Parameter']['Value']
        print("start getting ssm parameter ....")
        print(token_image_url)


        
        ### generate JSON metadata
        print("start calling safe_mint for issue card")
        mintResp =  smart_contract_helper.safe_mint(to_wallet_address,app_no)
        metadata = {}
        metadata['name'] = "Scolaire Token"
        metadata['description'] = "This is a student record NFT"
        metadata['image'] = token_image_url +'/' + str(mintResp["tokenID"])
        metadata['tokenId'] = mintResp["tokenID"]


        

        ### combine jpg
        # Download files from S3
        print("Download files from S3")

        s3 = boto3.client('s3')
        bucket_name = public_bucket_name
  
        font_file = s3.get_object(Bucket=private_bucket_name, Key='CARD_DATA/OpenSans-Semibold.ttf')['Body'].read()
        
        photo_file = s3.get_object(Bucket=private_bucket_name, Key= photo_path)['Body'].read()


        st_no_formatted_str =""
        ddbCardkey=""
        if institution == 'UWL':
            print("Created Student Card for UWL")

            template_file = s3.get_object(Bucket=private_bucket_name, Key='CARD_DATA/UWL_CARD_TEMPLATE.png')['Body'].read()

            # student number 
            st_num_str = str(mintResp["tokenID"])

            # Pad the string with leading zeros if necessary
            st_no_formatted_str = "U24" + st_num_str.zfill(5)
            print("student no: " + st_no_formatted_str)


            # Create the student card
            print("Create the student card")
            font = ImageFont.truetype(BytesIO(font_file), size=30)
            template = Image.open(BytesIO(template_file))
            pic = Image.open(BytesIO(photo_file)).resize((150, 190), Image.ADAPTIVE)
            template.paste(pic, (500, 110, 650, 300))
            draw = ImageDraw.Draw(template)
            draw.text((80, 220), surname + ' ' + given_name, font=font, fill='grey')
            draw.text((80, 265), st_no_formatted_str, font=font, fill='grey')
            draw.text((80, 310), mode_of_study, font=font, fill='grey')

            # Save the result to a BytesIO object
            print("Save the result to a BytesIO object")
            output_buffer = BytesIO()
            template.save(output_buffer, format='PNG')
            output_buffer.seek(0)

            ddbCardkey="uwl_scard_path"

        elif institution == 'HKIT':
            print("Created Student Card for HKIT")

            template_file = s3.get_object(Bucket=private_bucket_name, Key='CARD_DATA/HKIT_CARD_TEMPLATE.jpeg')['Body'].read()

            # student number 
            st_num_str = str(mintResp["tokenID"])

            # Pad the string with leading zeros if necessary
            st_no_formatted_str = "H24" + st_num_str.zfill(5)
            print("student no: " + st_no_formatted_str)

            # Create the student card
            print("Create the student card")
            font = ImageFont.truetype(BytesIO(font_file), size=30)
            template = Image.open(BytesIO(template_file))
            pic = Image.open(BytesIO(photo_file)).resize((145, 185), Image.ADAPTIVE)
            template.paste(pic, (500, 160, 645, 345))
            draw = ImageDraw.Draw(template)
            draw.text((80, 220), surname + ' ' + given_name, font=font, fill='grey')
            draw.text((80, 265), st_no_formatted_str, font=font, fill='grey')
            draw.text((80, 310), mode_of_study, font=font, fill='grey')

            # Save the result to a BytesIO object
            print("Save the result to a BytesIO for HKIT CARD object")
            output_buffer = BytesIO()
            template.save(output_buffer, format='PNG')
            output_buffer.seek(0)
            ddbCardkey="hkit_scard_path"
        else:
            raise Exception("Institution code not found")

        # append student no to metatdata json and Upload the metadata JSON data to S3
        metadata["studentId"] = st_no_formatted_str
        print(metadata)
        json_data = json.dumps(metadata)


        key = 'nft/SCOL' +  str(mintResp["tokenID"]) + '.json'

        s3.put_object(
            Body=json_data.encode('utf-8'),
            Bucket=bucket_name,
            Key=key
        )

        # Upload the resulting student card to S3
        outputCardFile='CARD_DATA/SCOL_IMG_' + st_num_str + '.png'
        
        s3.put_object(Bucket=private_bucket_name, Key=outputCardFile, Body=output_buffer)
        # upload_to_s3(private_bucket_name, outputCardFile, output_buffer)
        item = {
            'pk' : uid,
            'sk' : app_no,
            'status' : 'APPROVED-CARD-ISSUED',
        }
        item[ddbCardkey] = outputCardFile
        responseItem = dynamo.update_application(item)
        print(responseItem)


        msgid = message_helper.send_status_change(app_no,"APPROVED-CARD-ISSUED","")    
        print("Message sent to status update with id:" + msgid)



        return {
            "statusCode": 200,
            # "headers": {
            #     "Access-Control-Allow-Origin": "*",
            #     "Access-Control-Allow-Headers": "*",
            #     "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
            #      "Access-Control-Max-Age": "0"
            # },
            'body': json.dumps({'message': ' Mint Successfully!',
                                'tokenID' : mintResp["tokenID"],
                                'studentID' : st_no_formatted_str })
        }
        
    except Exception as e:
        print(e)
        # return {"statusCode": 500, "headers": {}, "body": "Internal Server Error"}
        return {
            'statusCode': 500,
            # "headers": {
            #     "Access-Control-Allow-Origin": "*",
            #     "Access-Control-Allow-Headers": "*",
            #     "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
            #      "Access-Control-Max-Age": "0"
            # },
            'body': json.dumps({'error': str(e)})
        }