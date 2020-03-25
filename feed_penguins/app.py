import json
import urllib3
import os
import uuid


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
    path = event['path']
    http_method = event['httpMethod']
    if "/list" == path:
        return handle_list(event, context)
    elif ("/attempt_charge" == path) and ("POST" == http_method):
        return handle_attempt_charge(event, context, generate_uuid, http_client, env)
    else:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": f'Unrecognized path: {path}'
            }),
        }


def handle_list(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps({
            "penguins": list_penguins()
        }),
    }


def handle_attempt_charge(event, context, generate_uuid, http_client, env):
    square_key = env["SQUARE_APP_KEY"]
    event_body = json.loads(event["body"])
    penguin_id = event_body["penguinId"]
    penguin = get_penguin_by_id(penguin_id)
    if penguin is None:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": f'Invalid penguin ID: {penguin_id}'
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
    if response.status in range(200,300):
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": f"Success!",
                "penguinId": penguin_id,
                "penguinName": penguin["name"],
                "chargeAmount": penguin["amount"]
            }),
        }
    else:
        print("*** Square API error: ***")
        print(response.status)
        print(response.headers)
        print(response.data)
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Square API error"})
        }
