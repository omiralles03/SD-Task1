from redis.exceptions import ExecAbortError
from common.config import RABBIT_HOST
from common.database import TicketDB

import pika
import json

def format_result_msg(result):
    status = result['status']
    msg = f" [<-] Result: {result['status']}"

    details = {
        "SUCCESS": lambda r: f" (Ticket #: {r.get('ticket')})",
        "CONFIRMED": lambda r: f" (Ticket #: {r.get('ticket')} already yours ({r.get('owner')})",
        "ALREADY_PROCESSED": lambda r: f" (Owned by: {r.get('owner')})",
        "OCCUPIED": lambda r: f" (Seat {r.get('seat_id')} owned by {r.get('owner')})",
        "INVALID_SEAT": lambda r: f" (Seat {r.get('seat_id')} out of range. Limit: 1 - {r.get('limit')})",
        "SOLD_OUT": lambda r: f" (Limit {r.get('limit')} reached (current: {r.get('current')})"
    }
    
    if status in details:
        msg += details[status](result)
    
    return msg


# Called everytime a message arrives from RabbitMQ
# Parses the JSON message from the queue and calls the correct DB method
def callback(channel, method, properties, body):

    try:
        data = json.loads(body)
        db = TicketDB()

        proc_msg = f" [->] Processing: {data['request_id']} for {data['client_id']}"


        if data['action'] == 'buy_numbered':
            proc_msg += f" with seat {data['seat_id']}"

            result = db.buy_numbered(
                client_id=data['client_id'],
                seat_id=data['seat_id'],
                request_id=data['request_id']
            )
        else:
            result = db.buy_unnumbered(
                client_id=data['client_id'],
                request_id=data['request_id']
            )

        print(proc_msg)
        print(format_result_msg(result))

        # Tells RabbitMQ the message was processed and can be deleted
        channel.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        # Do not acknowledge in case of error
        print(f" [!] Error: {e}")

def start_consumer():
    # Blocking Connection waits for established connections
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBIT_HOST))

    channel = connection.channel()
    channel.queue_declare(queue='ticket_queue', durable=True)

    # Dont give more than 1 message to a worker
    # until it has processed and acknowledged the previous one
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='ticket_queue', on_message_callback=callback)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == "__main__":
    start_consumer()
