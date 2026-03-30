import pika
import json

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

message = {
    "action": "buy_numbered",
    "client_id": "test_user_001",
    "seat_id": "99",
    "request_id": "test_req_555"
}

channel.basic_publish(
    exchange='',
    routing_key='ticket_queue',
    body=json.dumps(message)
)

print(" [x] Sent test message!")
connection.close()
