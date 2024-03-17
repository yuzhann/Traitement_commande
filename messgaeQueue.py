import pika
import json
from client import handle_confirm_order


def send_message(queue_name, message):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue=queue_name)
    channel.basic_publish(exchange='',
                          routing_key=queue_name,
                          body=message)
    print("Sent estimate")

    connection.close()


# receive message from server and send result to client
def receive_message(queue_name):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    def callback(ch, method, properties, body):
        order_info = json.loads(body)
        order_id = order_info['order_id']
        estimate = order_info['estimate']
        if estimate == 0:
            handle_confirm_order(order_id, 3)
        else:
            print(f"receive: {body}")
            choice = input("Received an order. Enter '1' to confirm or '2' to decline: ")
            handle_confirm_order(order_id, choice)

        connection.close()

    channel.queue_declare(queue=queue_name)
    channel.basic_consume(queue=queue_name,
                          on_message_callback=callback,
                          auto_ack=True)

    channel.start_consuming()
