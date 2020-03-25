import json
import urllib3
import os
import uuid

# import requests


def lambda_handler(event, context,
                   generate_uuid=uuid.uuid1,
                   http_client=urllib3.PoolManager(),
                   env=os.environ):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    # try:
    #     ip = requests.get("http://checkip.amazonaws.com/")
    # except requests.RequestException as e:
    #     # Send some context about this error to Lambda Logs
    #     print(e)

    #     raise e
    path = event['path']
    httpMethod = event['httpMethod']
    if "/list" == path:
        return handleList(event, context)
    elif ("/attempt_charge" == path) and ("POST" == httpMethod):
        return handleAttemptCharge(event, context, generate_uuid, http_client, env)
    else:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": f'Unrecognized path: {path}'
            }),
        }
    return


def handleList(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps({
            "penguins": [
                {'id': 1},
                {'id': 2},
                {'id': 3}
            ]
        }),
    }


def handleAttemptCharge(event, context, generate_uuid, http_client, env):
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "TODO"
        }),
    }
