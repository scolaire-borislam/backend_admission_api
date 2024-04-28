from web3 import Web3
from web3.middleware import geth_poa_middleware
import json
import boto3


def connectWeb3():
    try:
        ssm = boto3.client('ssm')
        rpc_parameter = ssm.get_parameter(Name='admission_rpcurl', WithDecryption=True)
        rpc_url = rpc_parameter['Parameter']['Value']
        print(rpc_url)
        web3 = Web3(Web3.HTTPProvider(rpc_url))
        web3 = Web3(Web3.HTTPProvider(rpc_url))
        print(web3.is_connected())
        return web3
    except Exception as e:
        print(e)
        raise e  

def get_scolaire_contract(web3, abi_object_key):
    try:
        ssm = boto3.client('ssm')

        # wallet_add_parameter = ssm.get_parameter(Name='admission_wallet_address', WithDecryption=True)
        # wallet_add = wallet_add_parameter['Parameter']['Value']
        # wallet_key_parameter = ssm.get_parameter(Name='admission_wallet_key', WithDecryption=True)
        # wallet_key = wallet_key_parameter['Parameter']['Value']
        
        req_contract_parameter = ssm.get_parameter(Name='admission_req_check_contract_address', WithDecryption=True)
        req_contract_address = req_contract_parameter['Parameter']['Value']
        
        bucket_parameter = ssm.get_parameter(Name='admission_bucket', WithDecryption=True)
        bucket_name = bucket_parameter['Parameter']['Value']

        # rpc_check_ai_parmeter = ssm.get_parameter(Name='admission_req_check_ai_url', WithDecryption=True)
        # rpc_check_ai_url = rpc_check_ai_parmeter['Parameter']['Value']

        print("start getting ssm parameter ....")


        # print(req_contract_address)
        print(bucket_name)
        # print(rpc_check_ai_url)

        s3 = boto3.client('s3')
        # abi_object_key = 'CONTRACT/ScolaireApplication.json'
        abi_response = s3.get_object(Bucket=bucket_name, Key=abi_object_key)
        abi_content = json.loads(abi_response['Body'].read().decode('utf-8'))
        print("abi_content")
        print(abi_content['abi'])

        print(" *******************" + req_contract_address)
        contract = web3.eth.contract(address=req_contract_address, abi=abi_content['abi'])
        
        return contract
    except Exception as e:
        print(e)
        raise e  



def update_contract_status( app_id, status,check_result):
    try:
        print('Start send SQS for contract status update')
        ssm = boto3.client('ssm')

        wallet_add_parameter = ssm.get_parameter(Name='admission_wallet_address', WithDecryption=True)
        wallet_add = wallet_add_parameter['Parameter']['Value']
        wallet_key_parameter = ssm.get_parameter(Name='admission_wallet_key', WithDecryption=True)
        wallet_key = wallet_key_parameter['Parameter']['Value']
        chain_id_parmeter = ssm.get_parameter(Name='admission_chain_id', WithDecryption=True)
        chain_id = int(chain_id_parmeter['Parameter']['Value'])
        print(chain_id)

        web3 = connectWeb3() 
        abi_object_key = 'CONTRACT/ScolaireApplication.json'

        print("start retrieving wallet ....")
        print(wallet_add)
        # print(wallet_key)
        balance = web3.eth.get_balance(wallet_add)
        print(web3.from_wei(balance, "ether"))
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        


        contract = get_scolaire_contract(web3,abi_object_key)
        nonce = web3.eth.get_transaction_count(wallet_add)
        tx = contract.functions.updateStatus(app_id, status, check_result).build_transaction({
            'chainId': chain_id,  # Polygon network ID
            'gas': 5000000,
            'gasPrice': web3.to_wei('20', 'gwei'),
            'nonce': nonce,
        })
        print("3 *******************")
        signed_tx = web3.eth.account.sign_transaction(tx, wallet_key)
        print("4 *******************")
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        hex_tx_hash = web3.to_hex(tx_hash)
        
        print(hex_tx_hash)
        print("5 ******************* end of update transaction")
        return hex_tx_hash
    except Exception as e:
        print(e)   
        raise e     
    

def req_check( email, app_id):

        try:
            print('Start send SQS for requirement check in smart contract')            
            ssm = boto3.client('ssm')

            wallet_add_parameter = ssm.get_parameter(Name='admission_wallet_address', WithDecryption=True)
            wallet_add = wallet_add_parameter['Parameter']['Value']
            wallet_key_parameter = ssm.get_parameter(Name='admission_wallet_key', WithDecryption=True)
            wallet_key = wallet_key_parameter['Parameter']['Value']
            rpc_check_ai_parmeter = ssm.get_parameter(Name='admission_req_check_ai_url', WithDecryption=True)
            rpc_check_ai_url = rpc_check_ai_parmeter['Parameter']['Value']
            chain_id_parmeter = ssm.get_parameter(Name='admission_chain_id', WithDecryption=True)
            chain_id = int(chain_id_parmeter['Parameter']['Value'])
            chainlink_sub_id_parmeter = ssm.get_parameter(Name='admission_chainlink_sub_id', WithDecryption=True)
            chainlink_sub_id = int(chainlink_sub_id_parmeter['Parameter']['Value'])
            print(chain_id)
            print(chainlink_sub_id)

            web3 = connectWeb3() 
            abi_object_key = 'CONTRACT/ScolaireApplication.json'

            print("start retrieving wallet ....")
            print(wallet_add)
            # print(wallet_key)
            balance = web3.eth.get_balance(wallet_add)
            print(web3.from_wei(balance, "ether"))
            web3.middleware_onion.inject(geth_poa_middleware, layer=0)
            

            contract = get_scolaire_contract(web3,abi_object_key)
            nonce = web3.eth.get_transaction_count(wallet_add)
    

            # sendRequest to requirement check smart contract
            args = [email,app_id,rpc_check_ai_url]
            chainlinSubscriptionId = chainlink_sub_id
            tx = contract.functions.sendRequest(chainlinSubscriptionId,args).build_transaction({
                'chainId': chain_id,  # Polygon network ID
                'gas': 5000000,
                'gasPrice': web3.to_wei('20', 'gwei'),
                'nonce': nonce,
            })
            print("******************* sign tran")
            signed_tx = web3.eth.account.sign_transaction(tx, wallet_key)
            print("******************* send tran")
            tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            hex_tx_hash = web3.to_hex(tx_hash)
            
            print(hex_tx_hash)
            print(" ******************* end of requirement check transaction")
            return hex_tx_hash

        except Exception as e:
            print(e)   
            raise e     
        

def get_scolaire_token_contract(web3, abi_object_key):
    try:
        ssm = boto3.client('ssm')
  
        token_contract_parameter = ssm.get_parameter(Name='admission_contract_address', WithDecryption=True)
        token_contract_address = token_contract_parameter['Parameter']['Value']
        
        bucket_parameter = ssm.get_parameter(Name='admission_bucket', WithDecryption=True)
        bucket_name = bucket_parameter['Parameter']['Value']

        print("start getting ssm parameter ....")
        print(bucket_name)

        s3 = boto3.client('s3')

        abi_response = s3.get_object(Bucket=bucket_name, Key=abi_object_key)
        abi_content = json.loads(abi_response['Body'].read().decode('utf-8'))
        print("abi_content")
        print(abi_content['abi'])

        print(" *******************" + token_contract_address)
        contract = web3.eth.contract(address=token_contract_address, abi=abi_content['abi'])
        
        return contract
    except Exception as e:
        print(e)
        raise e  


def safe_mint(to_addr, app_id):

        try:
            print('Start safe mint NFT in smart contract')            
            ssm = boto3.client('ssm')

            wallet_add_parameter = ssm.get_parameter(Name='admission_wallet_address', WithDecryption=True)
            wallet_add = wallet_add_parameter['Parameter']['Value']
            wallet_key_parameter = ssm.get_parameter(Name='admission_wallet_key', WithDecryption=True)
            wallet_key = wallet_key_parameter['Parameter']['Value']
            # rpc_check_ai_parmeter = ssm.get_parameter(Name='admission_req_check_ai_url', WithDecryption=True)
            # rpc_check_ai_url = rpc_check_ai_parmeter['Parameter']['Value']
            chain_id_parmeter = ssm.get_parameter(Name='admission_chain_id', WithDecryption=True)
            chain_id = int(chain_id_parmeter['Parameter']['Value'])

            print(chain_id)
            web3 = connectWeb3() 
            abi_object_key = 'CONTRACT/Scolaire.json'

            print("start retrieving wallet ....")
            print(wallet_add)
            # print(wallet_key)
            balance = web3.eth.get_balance(wallet_add)
            print(web3.from_wei(balance, "ether"))
            web3.middleware_onion.inject(geth_poa_middleware, layer=0)
            

            tokenContract = get_scolaire_token_contract(web3,abi_object_key)
            nonce = web3.eth.get_transaction_count(wallet_add)
    

            # sendRequest to requirement check smart contract
            tx = tokenContract.functions.safeMint(Web3.to_checksum_address(to_addr),app_id).build_transaction({
                'chainId': chain_id,  # Polygon or ethereum network ID
                'gas': 5000000,
                'gasPrice': web3.to_wei('20', 'gwei'),
                'nonce': nonce,
            })
            print("******************* sign tran")
            signed_tx = web3.eth.account.sign_transaction(tx, wallet_key)
            print("******************* send tran")
            tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            hex_tx_hash = web3.to_hex(tx_hash)
            
            print(hex_tx_hash)
            print(f"NFT minted! Transaction hash: {hex_tx_hash}")

            # Wait for the transaction to be mined
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            
            print(tx_receipt)
            # Check if the SafeMint event was emitted
            safe_mint_event = tokenContract.events.SafeMint().process_receipt(tx_receipt)
            print("after wait for event")
            if safe_mint_event:
                eventRespDict = {}
                # Get the parameters from the event
                for event in safe_mint_event:
                    print(f"Token ID: {event['args']['tokenID']}")
                    print(f"Token URI: {event['args']['tokenURI']}")
                    eventRespDict['tokenID'] = event['args']['tokenID']
                    eventRespDict['tokenURI'] = event['args']['tokenURI']
                    # Access other event parameters as needed
                return eventRespDict
            else:
                print("SafeMint event not emitted")
                raise Exception("afeMint event not emitted")


        except Exception as e:
            print(e)   
            raise e     