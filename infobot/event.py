import json
import os
import re
import boto3
from boto3.dynamodb.conditions import Key
from slackclient import SlackClient

BOT_TOKEN = os.environ['BOT_TOKEN']
FACTOID_TABLE = os.environ['FACTOID_TABLE']
sc = SlackClient(BOT_TOKEN)
ddb = boto3.resource('dynamodb')
factoid_table = ddb.Table(FACTOID_TABLE)

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
    the_text = data["event"]["text"]

    # some silliness
    p = re.compile(r"ura \w*")
    m = p.findall(the_text)
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
        the_text.find("is") > 0 and
        the_text[-1] is not "?"
    ):
        the_text_as_list = the_text.split()
        the_subject = the_text_as_list[the_text_as_list.index("is")-1]
        the_fact = the_text[the_text.find("is")+3:]
        put_factoid(the_subject, the_fact)

def put_factoid(subject, fact):
    print("the factoid: {0} is {1}".format(subject, fact))
    item = {
        "subject": subject.lower(),
        "fact": fact.lower()
    }
    response = factoid_table.put_item(Item=item)
    print(response)