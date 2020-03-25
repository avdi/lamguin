import json
import urllib3
import os
import uuid

# import requests

def list_penguins():
    return [
        {'id': 1, 'name': "Emperor Penguin", 'amount': 300,
         'image_uri': "https://feed-penguins.s3.amazonaws.com/emperor.jpg"},
        {'id': 2, 'name': "Chinstrap Penguin", 'amount': 500,
         'image_uri': "https://feed-penguins.s3.amazonaws.com/chinstrap.jpg"},
        {'id': 3, 'name': "Rockhopper Penguin", 'amount': 700,
         'image_uri': "https://feed-penguins.s3.amazonaws.com/rockhopper.jpg"}
    ]


def get_penguin_by_id(penguin_id):
    return next((p for p in list_penguins() if p['id'] == penguin_id), None)


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
    square_key = env["SQUARE_APP_KEY"]
    event_body = json.loads(event["body"])
    penguinId = event_body["penguinId"]
    penguin = get_penguin_by_id(penguinId)
    if penguin is None:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": f'Invalid penguin ID: {penguinId}'
            }),
        }
    post_data = {
        "idempotency_key": generate_uuid().urn,
        "source_id": event_body['nonce'],
        "amount_money": {
            "amount": penguin['amount'],
            "currency": "USD"
        }
    }
    post_body = json.dumps(post_data)
    response = http_client.request(
        "POST",
        "https://connect.squareupsandbox.com/v2/payments",
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {square_key}'
        },
        body=post_body)
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": f"Success!",
            "penguinId": penguinId,
            "penguinName": penguin["name"],
            "chargeAmount": penguin["amount"]
        }),
    }
