import json
import os
import boto3
from boto3.dynamodb.conditions import Key
from slackclient import SlackClient

BOT_TOKEN = os.environ['BOT_TOKEN']
SENTIMENTS_TRACKER_TABLE = os.environ['SENTIMENTS_TRACKER_TABLE']
FEATUREFLAG_TABLE = os.environ['FEATUREFLAG_TABLE']

sc = SlackClient(BOT_TOKEN)
ddb = boto3.resource('dynamodb')
comprehend = boto3.client('comprehend')
sentiments_tracker_table = ddb.Table(SENTIMENTS_TRACKER_TABLE)
featureflag_table = ddb.Table(FEATUREFLAG_TABLE)

def receive(event, context):
    data = json.loads(event['body'])
    #print("Got data: {}".format(data))
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
    # get the sentiment
    sentiment = get_sentiment(data["event"]["text"])

    # store the sentiment
    store_sentiment_response = store_sentiment_count(sentiment, data["event"]["user"], data["event"]["ts"])

    # add reactions to slack
    feature_enabled = check_feature_flag("sentiment_reactions")
    if feature_enabled:
        reaction = get_reaction(sentiment)
        reaction_response = send_reaction(data["event"]["channel"], reaction, data["event"]["ts"])
        print(reaction_response)
    else:
        print("sentiment_reactions was disabled")

def get_sentiment(text):
    sentiment = comprehend.detect_sentiment(
        Text=text,
        LanguageCode='en'
    )
    return(sentiment['Sentiment'])

def get_reaction(sentiment):
    if sentiment == "POSITIVE":
        reaction = "thumbsup"
    elif sentiment == "NEGATIVE":
        reaction = "thumbsdown"
    elif sentiment == "NEUTRAL":
        reaction = "neutral_face"
    elif sentiment == "MIXED":
        reaction = "shrug"
    return(reaction)

def send_reaction(channel, reaction, timestamp):
    response = sc.api_call(
        "reactions.add",
        channel=channel,
        name=reaction,
        timestamp=timestamp
    )
    return(response['ok'])

def check_feature_flag(feature):
    response = featureflag_table.get_item(
        Key={
            'feature': feature
        }
    )
    return(response['Item']['enabled'])

def store_sentiment_count(sentiment, subject, timestamp):
    response = sentiments_tracker_table.put_item(
        Item={
            'subject': subject,
            'sentiment': sentiment,
            'timestamp': timestamp
        }
    )
    return(response)