import json
import os

BOT_TOKEN = os.environ['BOT_TOKEN']

def receive(event, context):
    data = json.loads(event['body'])
    print("Got data: {}".format(data))
    return_body = "ok"

    if data["type"] == "url_verification":
        print("Received challenge")
        return_body = data["challenge"]

    return {
        "statusCode": 200,
        "body": return_body
    }