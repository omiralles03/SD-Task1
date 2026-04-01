from redis.exceptions import ExecAbortError
from common.config import RABBIT_HOST
from common.database import TicketDB
from common.parser import format_result_msg

import pika
import json
import time
import os
import socket

db = TicketDB()
start_time = None
count = 0
consumer_id = socket.gethostname()

# Called everytime a message arrives from RabbitMQ
# Parses the JSON message from the queue and calls the correct DB method
def callback(channel, method, properties, body):
    global start_time, count, consumer_id

    try:
        data = json.loads(body)

        # --- BENCHMARK ---
        if data['action'] == 'START':
            start_time = time.perf_counter()
            count = 0
            channel.basic_ack(delivery_tag=method.delivery_tag)
            return

        # Delay start (if consumer joined late the queue)
        if start_time is None and data['action'] not in ['START', 'FINISH']:
            start_time = time.perf_counter()
            count = 0

        if data['action'] == 'FINISH':
            if start_time is not None:
                elapsed = time.perf_counter() - start_time
                print(f"c-{consumer_id}: [v] Processed {count} requests...")
                print(f"c-{consumer_id}: [>] Total time: {elapsed:.2f} s")
                print(f"c-{consumer_id}: [>] Throughput: {count/elapsed:.2f} ops/s")
                channel.basic_ack(delivery_tag=method.delivery_tag)
                start_time = None
                count = 0
            return
        # --- BENCHMARK ---

        proc_msg = f"c-{consumer_id}: [->] Processing: {data['request_id']} for {data['client_id']}"

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
        count += 1
        channel.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        # Do not acknowledge in case of error
        print(f"c-{consumer_id}: [!] Error: {e}")

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
