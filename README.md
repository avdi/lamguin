This is a demo for the server side of a mobile app using the Square payment SDK.

## Updating Environment Variables
```shell script
aws --region us-east-1 lambda update-function-configuration \
    --function-name lamguin-FeedPenguinsFunction-1A9529C4LZEAZ \
    --environment "Variables={SQUARE_APP_ID=...,SQUARE_APP_KEY=...}"
```