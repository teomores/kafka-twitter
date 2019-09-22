from flask import Flask, request, Response
app = Flask(__name__)

from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer
import requests
import time
import json
from confluent_kafka import KafkaError
from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError
from confluent_kafka import TopicPartition
import time
import datetime
from flask import stream_with_context, request, Response

# defaults
TOPIC = 'esame5'
BOOTSTRAP_SERVERS = 'localhost:9092' # this will be distributed...
SCHEMA_REGISTRY_URL = 'http://127.0.0.1:8081'
KEY_SCHEMA = avro.loads(open('key_schema.avsc', 'r', newline='').read())
VALUE_SCHEMA = avro.loads(open('tweet_avro_schema.avsc', 'r', newline='').read())
WINDOW_LEN = 30
STREAMING_WINDOW_SECONDS = 30

# Subscription URL
@app.route('/users/id', methods=['POST'])
def subscribe():
    id = request.form['id']
    # create consumer and producer
    c = AvroConsumer(
        {
        'bootstrap.servers': BOOTSTRAP_SERVERS,
        'group.id': f'{id}',
        'schema.registry.url': SCHEMA_REGISTRY_URL
        }
    )
    # assign the partition
    c.subscribe([TOPIC])
    #c.assign([TopicPartition(TOPIC, 0,0)])
    print(f"Assignments: {c.assignment()}")

    return f"Logged in as {id}"

# Publish URL
@app.route('/tweet', methods=['POST'])
def produce_tweet():
    if 'username' in request.cookies:
        id = request.form['id']
        content = request.form['content']
        location = request.form['location']
        # extract tags and mentions :)
        tags = [h for h in content.split() if h.startswith('#')]
        mentions = [h for h in content.split() if h.startswith('@')]

        value = {
            "author": f"{id}",
            "content": f"{content}",
            "timestamp": f"{time.time()}",
            "location": f"{location}",
            "tags": tags,
            "mentions": mentions
        }
        key = {"name": f"{id}"}

        p = AvroProducer({
            'bootstrap.servers': BOOTSTRAP_SERVERS,
            'enable.idempotence': 'true', # for EOS: assures that only one tweet in sent
            'schema.registry.url': SCHEMA_REGISTRY_URL
            }, default_key_schema=KEY_SCHEMA, default_value_schema=VALUE_SCHEMA)

        p.produce(topic=TOPIC, value=value, key=key)
        p.flush()
        return 'Tweet published!'
    else:
        return 'Oooops, your are not logged in...'


# Batch (with filtering) URL
@app.route('/tweets/cityfilter=<cityfilter>&mentionfilter=<mentionfilter>&tagfilter=<tagfilter>/latest', methods=['GET'])
def batch_filtering(cityfilter='ALL', mentionfilter='ALL', tagfilter='ALL'):
    if 'username' in request.cookies:
        username = request.cookies['username']
        print(f"Ok, {username}, let's fetch the latest tweets!")
        c = AvroConsumer(
            {
            'bootstrap.servers': BOOTSTRAP_SERVERS,
            'group.id': username,
            'schema.registry.url': SCHEMA_REGISTRY_URL,
            #'isolation.level': 'read_committed'
            }
        )
        c.assign([TopicPartition(TOPIC, 0,0)])
        low_offset, high_offset = c.get_watermark_offsets(TopicPartition(TOPIC, 0))
        #print(f"the latest offset is {high_offset}, the low is {low_offset}")

        # move consumer to offset=high_offset-WINDOW_LEN (only if > 0)
        if high_offset-WINDOW_LEN>0:
            new_offset = high_offset-WINDOW_LEN
        else:
            new_offset = low_offset
        c.seek(TopicPartition(TOPIC, 0, new_offset))

        msgs = [] # to store the messages to be returned
        pos = c.position([TopicPartition(TOPIC, 0, new_offset)])
        while pos[0].offset<high_offset:
            try:
                msg = c.poll(0)

            except SerializerError as e:
                print("Message deserialization failed for {}: {}".format(msg, e))
                break

            if msg is None:
                continue

            if msg.error():
                print("AvroConsumer error: {}".format(msg.error()))
                continue

            author = msg.value()['author']
            content = msg.value()['content']
            #kafka_timestamp = datetime.datetime.fromtimestamp(float(msg.timestamp()[1]/1000)).strftime('%H:%M:%S, %d-%m-%Y')
            timestamp = datetime.datetime.fromtimestamp(float(msg.value()['timestamp'])).strftime('%H:%M:%S, %d-%m-%Y')
            message_ts = float(msg.value()['timestamp'])
            location = msg.value()['location']
            tags = [h[1:] for h in content.split() if h.startswith('#')]
            mentions = [h[1:] for h in content.split() if h.startswith('@')]
            display_message = f"[{author}] {content} ({location} - {timestamp})"
            print(f"[{author}] {content} ({location} - {timestamp})")
            #print(f"consumer position: {c.position([TopicPartition(TOPIC, 0, new_offset)])}")
            pos = c.position([TopicPartition(TOPIC, 0, new_offset)])

            if cityfilter!='ALL' and mentionfilter!='ALL' and tagfilter!='ALL':
                if (location.lower() == cityfilter) and (mentionfilter.lower() in mentions) and (tagfilter.lower() in tags):
                    msgs.append((display_message,message_ts))
            elif cityfilter=='ALL' and mentionfilter!='ALL' and tagfilter!='ALL':
                if (mentionfilter.lower() in mentions) and (tagfilter.lower() in tags):
                    msgs.append((display_message,message_ts))
            elif cityfilter!='ALL' and mentionfilter=='ALL' and tagfilter!='ALL':
                if (location.lower() == cityfilter) and (tagfilter.lower() in tags):
                    msgs.append((display_message,message_ts))
            elif cityfilter!='ALL' and mentionfilter!='ALL' and tagfilter=='ALL':
                if (location.lower() == cityfilter) and (mentionfilter.lower() in mentions):
                    msgs.append((display_message,message_ts))
            elif cityfilter!='ALL' and mentionfilter=='ALL' and tagfilter=='ALL':
                if (location.lower() == cityfilter):
                    msgs.append((display_message,message_ts))
            elif cityfilter=='ALL' and mentionfilter!='ALL' and tagfilter=='ALL':
                if (mentionfilter.lower() in mentions):
                    msgs.append((display_message,message_ts))
            elif cityfilter=='ALL' and mentionfilter=='ALL' and tagfilter!='ALL':
                if (tagfilter.lower() in tags):
                    msgs.append((display_message,message_ts))
            else:
                msgs.append((display_message,message_ts))
        c.close()
        # finally return dictonary of messages
        msgs = list(set(msgs)) # this is done to ensure that no duplicates of a message are shown in timeline
        msgs = sorted(msgs, key=lambda x: x[1])
        msgs = [m[0] for m in msgs]
        print(msgs)
        return {"results": msgs}
    else:
        return {"results": ['Oooops, your are not logged in...']}

# Streaming (with filters) URL
@app.route('/tweets/streaming', methods=['POST'])
def streaming_filtering():
    cityfilter = request.form['cityfilter']
    mentionfilter = request.form['mentionfilter']
    tagfilter = request.form['tagfilter']
    print(f'cityfilter: {cityfilter}')
    print(f'mentionfilter: {mentionfilter}')
    print(f'tagfilter: {tagfilter}')

    if 'username' in request.cookies:
        username = request.cookies['username']
        print(f"Ok, {username}, let's stream the latest tweets!")
        c = AvroConsumer(
            {
            'bootstrap.servers': BOOTSTRAP_SERVERS,
            'group.id': username,
            'schema.registry.url': SCHEMA_REGISTRY_URL
            }
        )
        c.assign([TopicPartition(TOPIC, 0,0)])
        low_offset, high_offset = c.get_watermark_offsets(TopicPartition(TOPIC, 0))
        print(f"the latest offset is {high_offset}, the low is {low_offset}")
        print(f"consumer position: {c.position([TopicPartition(TOPIC, 0)])}")

        # move consumer to top
        c.seek(TopicPartition(TOPIC, 0, high_offset))

        msgs = []
        pos = c.position([TopicPartition(TOPIC, 0, high_offset)])
        def gen(msgs): # generator funciton for streaming
            print('ciao')
            while True:
                try:
                    msg = c.poll(1)

                except SerializerError as e:
                    print("Message deserialization failed for {}: {}".format(msg, e))
                    break

                if msg is None:
                    current_ts = time.time()
                    msgs = [m for m in msgs if (float(current_ts)-float(m[1]))<STREAMING_WINDOW_SECONDS]
                    ret_msgs = [m[0] for m in msgs]
                    yield f' `{json.dumps(ret_msgs)}` '
                    continue

                if msg.error():
                    current_ts = time.time()
                    msgs = [m for m in msgs if (float(current_ts)-float(m[1]))<STREAMING_WINDOW_SECONDS]
                    ret_msgs = [m[0] for m in msgs]
                    yield f' `{json.dumps(ret_msgs)}` '
                    print("AvroConsumer error: {}".format(msg.error()))
                    continue

                # get message fields
                author = msg.value()['author']
                content = msg.value()['content']
                #kafka_timestamp = datetime.datetime.fromtimestamp(float(msg.timestamp()[1]/1000)).strftime('%H:%M:%S, %d-%m-%Y')
                timestamp = datetime.datetime.fromtimestamp(float(msg.value()['timestamp'])).strftime('%H:%M:%S, %d-%m-%Y')
                location = msg.value()['location']
                tags = [h[1:] for h in content.split() if h.startswith('#')]
                mentions = [h[1:] for h in content.split() if h.startswith('@')]
                # create display_message
                display_message = f"[{author}] {content} ({location} - {timestamp})"
                display_message = display_message.replace("`", "'") # serve per leggere lo streaming
                message_ts = float(msg.value()['timestamp'])
                print(f"{display_message}")
                print(f"consumer position: {c.position([TopicPartition(TOPIC, 0, high_offset)])}")
                pos = c.position([TopicPartition(TOPIC, 0, high_offset)])
                print('prima')
                print(f'cityfilter: {cityfilter}')
                print(f'mentionfilter: {mentionfilter}')
                print(f'tagfilter: {tagfilter}')

                if cityfilter!='ALL' and mentionfilter!='ALL' and tagfilter!='ALL':
                    if (location.lower() == cityfilter) and (mentionfilter.lower() in mentions) and (tagfilter.lower() in tags):
                        msgs.append((display_message,message_ts))
                elif cityfilter=='ALL' and mentionfilter!='ALL' and tagfilter!='ALL':
                    if (mentionfilter.lower() in mentions) and (tagfilter.lower() in tags):
                        msgs.append((display_message,message_ts))
                elif cityfilter!='ALL' and mentionfilter=='ALL' and tagfilter!='ALL':
                    if (location.lower() == cityfilter) and (tagfilter.lower() in tags):
                        msgs.append((display_message,message_ts))
                elif cityfilter!='ALL' and mentionfilter!='ALL' and tagfilter=='ALL':
                    if (location.lower() == cityfilter) and (mentionfilter.lower() in mentions):
                        msgs.append((display_message,message_ts))
                elif cityfilter!='ALL' and mentionfilter=='ALL' and tagfilter=='ALL':
                    if (location.lower() == cityfilter):
                        msgs.append((display_message,message_ts))
                elif cityfilter=='ALL' and mentionfilter!='ALL' and tagfilter=='ALL':
                    if (mentionfilter.lower() in mentions):
                        msgs.append((display_message,message_ts))
                elif cityfilter=='ALL' and mentionfilter=='ALL' and tagfilter!='ALL':
                    if (tagfilter.lower() in tags):
                        msgs.append((display_message,message_ts))
                else:
                    msgs.append((display_message,message_ts))

                # remove old messages
                current_ts = time.time()
                msgs = [m for m in msgs if (float(current_ts)-float(m[1]))<STREAMING_WINDOW_SECONDS]
                #msgs = list(set(msgs))
                msgs = sorted(msgs, key=lambda x: x[1])
                ret_msgs = [m[0] for m in msgs]
                yield f' `{json.dumps(ret_msgs)}` '

        return Response(stream_with_context(gen(msgs)))
    else:
        return {"results": ['Oooops, your are not logged in...']}

if __name__ == '__main__':
    app.run(host='127.0.0.1', port='5000', debug=True)
