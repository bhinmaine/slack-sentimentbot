import json

def receive(event, context):
    data = json.loads(event['body'])
    print("Got data: {}".format(data))

    return {
        "statusCode": 200,
        "body": "ok"
    }