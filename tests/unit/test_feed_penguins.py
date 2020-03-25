import json
import urllib3
from types import SimpleNamespace

import pytest

from feed_penguins import app


@pytest.fixture()
def list_penguins_event():
    """ Generates API GW List Event"""

    return {
        "body": '{ }',
        "resource": "/{proxy+}",
        "requestContext": {
            "resourceId": "123456",
            "apiId": "1234567890",
            "resourcePath": "/{proxy+}",
            "httpMethod": "POST",
            "requestId": "c6af9ac6-7b61-11e6-9a41-93e8deadbeef",
            "accountId": "123456789012",
            "identity": {
                "apiKey": "",
                "userArn": "",
                "cognitoAuthenticationType": "",
                "caller": "",
                "userAgent": "Custom User Agent String",
                "user": "",
                "cognitoIdentityPoolId": "",
                "cognitoIdentityId": "",
                "cognitoAuthenticationProvider": "",
                "sourceIp": "127.0.0.1",
                "accountId": "",
            },
            "stage": "prod",
        },
        "queryStringParameters": {"foo": "bar"},
        "headers": {
            "Via": "1.1 08f323deadbeefa7af34d5feb414ce27.cloudfront.net (CloudFront)",
            "Accept-Language": "en-US,en;q=0.8",
            "CloudFront-Is-Desktop-Viewer": "true",
            "CloudFront-Is-SmartTV-Viewer": "false",
            "CloudFront-Is-Mobile-Viewer": "false",
            "X-Forwarded-For": "127.0.0.1, 127.0.0.2",
            "CloudFront-Viewer-Country": "US",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Upgrade-Insecure-Requests": "1",
            "X-Forwarded-Port": "443",
            "Host": "1234567890.execute-api.us-east-1.amazonaws.com",
            "X-Forwarded-Proto": "https",
            "X-Amz-Cf-Id": "aaaaaaaaaae3VYQb9jd-nvCd-de396Uhbp027Y2JvkCPNLmGJHqlaA==",
            "CloudFront-Is-Tablet-Viewer": "false",
            "Cache-Control": "max-age=0",
            "User-Agent": "Custom User Agent String",
            "CloudFront-Forwarded-Proto": "https",
            "Accept-Encoding": "gzip, deflate, sdch",
        },
        "pathParameters": {"proxy": "/examplepath"},
        "httpMethod": "POST",
        "stageVariables": {"baz": "qux"},
        "path": "/list",
    }


@pytest.fixture()
def attempt_charge_event():
    """ Generates API GW AttemptCharge Event"""

    return {
        "body": '{ "nonce": "NONCE9876", "penguinId": 1 }',
        "resource": "/{proxy+}",
        "requestContext": {
            "resourceId": "123456",
            "apiId": "1234567890",
            "resourcePath": "/{proxy+}",
            "httpMethod": "POST",
            "requestId": "c6af9ac6-7b61-11e6-9a41-93e8deadbeef",
            "accountId": "123456789012",
            "identity": {
                "apiKey": "",
                "userArn": "",
                "cognitoAuthenticationType": "",
                "caller": "",
                "userAgent": "Custom User Agent String",
                "user": "",
                "cognitoIdentityPoolId": "",
                "cognitoIdentityId": "",
                "cognitoAuthenticationProvider": "",
                "sourceIp": "127.0.0.1",
                "accountId": "",
            },
            "stage": "prod",
        },
        "queryStringParameters": {"foo": "bar"},
        "headers": {
            "Via": "1.1 08f323deadbeefa7af34d5feb414ce27.cloudfront.net (CloudFront)",
            "Accept-Language": "en-US,en;q=0.8",
            "CloudFront-Is-Desktop-Viewer": "true",
            "CloudFront-Is-SmartTV-Viewer": "false",
            "CloudFront-Is-Mobile-Viewer": "false",
            "X-Forwarded-For": "127.0.0.1, 127.0.0.2",
            "CloudFront-Viewer-Country": "US",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Upgrade-Insecure-Requests": "1",
            "X-Forwarded-Port": "443",
            "Host": "1234567890.execute-api.us-east-1.amazonaws.com",
            "X-Forwarded-Proto": "https",
            "X-Amz-Cf-Id": "aaaaaaaaaae3VYQb9jd-nvCd-de396Uhbp027Y2JvkCPNLmGJHqlaA==",
            "CloudFront-Is-Tablet-Viewer": "false",
            "Cache-Control": "max-age=0",
            "User-Agent": "Custom User Agent String",
            "CloudFront-Forwarded-Proto": "https",
            "Accept-Encoding": "gzip, deflate, sdch",
        },
        "pathParameters": {"proxy": "/examplepath"},
        "httpMethod": "POST",
        "stageVariables": {"baz": "qux"},
        "path": "/attempt_charge",
    }


def test_list_penguins(list_penguins_event, mocker):
    ret = app.lambda_handler(list_penguins_event, "")
    data = json.loads(ret["body"])

    assert ret["statusCode"] == 200
    assert "penguins" in ret["body"]
    assert data["penguins"] == [
        {'id': 1},
        {'id': 2},
        {'id': 3}
    ]


def test_attempt_charge_with_get(attempt_charge_event, mocker):
    """ attempt_charge should only respond to POST """
    attempt_charge_event["httpMethod"] = "GET"

    ret = app.lambda_handler(attempt_charge_event, "")
    data = json.loads(ret["body"])

    assert 400 <= ret["statusCode"] < 500
    assert "message" in ret["body"]


def test_attempt_valid_charge(attempt_charge_event, mocker):
    """ attempt_charge """

    def fake_uuid(): return SimpleNamespace(urn="UUID1234")
    http_response = SimpleNamespace(status=200, headers={}, data="")
    http_client = mocker.Mock(urllib3.PoolManager(), name="http_client")
    http_client.request.return_value = http_response
    env = {"SQUARE_APP_KEY": "MOCK_KEY_123"}
    ret = app.lambda_handler(attempt_charge_event, "",
                             fake_uuid, http_client, env)
    expected_headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer MOCK_KEY_123'
    }
    expected_body = {
        "idempotency_key": "UUID1234",
        "source_id": "NONCE9876",
        "amount_money": {
            "amount": 300,
            "currency": "USD"
        }
    }
    http_client.request.assert_called_with(
        "POST", "https://connect.squareupsandbox.com/v2/payments",
        headers=expected_headers,
        body=json.dumps(expected_body))
    data = json.loads(ret["body"])

    assert 200 == ret["statusCode"]
    assert "message" in ret["body"]


def test_attempt_valid_charge_for_a_different_penguin(attempt_charge_event, mocker):
    def fake_uuid(): return SimpleNamespace(urn="UUID1234")
    http_response = SimpleNamespace(status=200, headers={}, data="")
    http_client = mocker.Mock(urllib3.PoolManager(), name="http_client")
    http_client.request.return_value = http_response
    env = {"SQUARE_APP_KEY": "MOCK_KEY_123"}
    attempt_charge_event["body"] = '{ "nonce": "NONCE9876", "penguinId": 2 }'
    ret = app.lambda_handler(attempt_charge_event, "",
                             fake_uuid, http_client, env)

    expected_headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer MOCK_KEY_123'
    }
    expected_body = {
        "idempotency_key": "UUID1234",
        "source_id": "NONCE9876",
        "amount_money": {
            "amount": 500,
            "currency": "USD"
        }
    }
    http_client.request.assert_called_with(
        "POST", "https://connect.squareupsandbox.com/v2/payments",
        headers=expected_headers,
        body=json.dumps(expected_body))
    data = json.loads(ret["body"])

    assert 200 == ret["statusCode"]
    assert "message" in ret["body"]
    assert data["chargeAmount"] == 500
    assert data["penguinName"] == "Chinstrap Penguin"
    assert data["penguinId"] == 2


def test_failed_charge(attempt_charge_event, mocker):
    def fake_uuid(): return SimpleNamespace(urn="UUID1234")
    http_response = SimpleNamespace(status=400, headers={}, data="")
    http_client = mocker.Mock(urllib3.PoolManager(), name="http_client")
    http_client.request.return_value = http_response
    env = {"SQUARE_APP_KEY": "MOCK_KEY_123"}
    ret = app.lambda_handler(attempt_charge_event, "",
                             fake_uuid, http_client, env)
    data = json.loads(ret["body"])

    assert 400 == ret["statusCode"]
