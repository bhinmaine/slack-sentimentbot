import json
import os
import re
from slackclient import SlackClient

BOT_TOKEN = os.environ['BOT_TOKEN']
sc = SlackClient(BOT_TOKEN)

def receive(event, context):
    data = json.loads(event['body'])
    print("Got data: {}".format(data))
    return_body = "ok"

    if data["type"] == "url_verification":
        print("Received challenge")
        return_body = data["challenge"]
    elif (
        data["type"] == "event_callback" and
        data["event"]["type"] == "message" and
        "subtype" not in data["event"]
    ):
        handle_message(data)

    return {
        "statusCode": 200,
        "body": return_body
    }

def handle_message(data):
    poster_user_id = data["event"]["user"]

    p = re.compile(r"ura bot")
    m = p.findall(data["event"]["text"])
    if m:
        for match in m:
            print(match)
            print(poster_user_id)
            sc.api_call(
                "chat.postMessage",
                channel="{}".format(data["event"]["channel"]),
                text="no, ura bot <@{}>".format(poster_user_id)
                )