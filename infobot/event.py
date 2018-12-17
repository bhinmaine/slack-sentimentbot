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
    # some silliness
    p = re.compile(r"ura \w*")
    m = p.findall(data["event"]["text"])
    if m:
        for match in m:
            split = match.split()
            sc.api_call(
                "chat.postMessage",
                channel="{}".format(data["event"]["channel"]),
                text="no, ura {0}".format(split[1])
                )
    # lets discover some factoids
    if (
        data["event"]["text"].find("is") > 0 and
        data["event"]["text"][-1] is not "?"
    ):
        the_text = data["event"]["text"]
        the_text_as_list = the_text.split()
        the_subject = the_text_as_list[the_text_as_list.index("is")-1]
        the_fact = the_text[the_text.find("is")+3:]
        print("the factoid: {0} is {1}".format(the_subject, the_fact))