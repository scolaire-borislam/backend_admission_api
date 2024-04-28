# Project of backend REST API for the Scolaire Ledger frontend and backend 

Tools for local development:

1. Docker Desktop
2. AWS CLI
3. AWS SAM CLI


create virutal environment:
```
python -m venv .venv
source .venv/bin/activate
pip install wheel 
```

Create Docker network for local development:
```
docker run -p 8000:8000 -d --rm --network lambda-local --name dynamodb -v c:/docker/dynamodb:/data/ amazon/dynamodb-local -jar DynamoDBLocal.jar -sharedDb -dbPath /data
```

Use sam CLI to build and run the project locally:
```
sam build
sam local start-api --docker-network lambda-local --parameter-overrides AWSENV=AWS_SAM_LOCAL
```
