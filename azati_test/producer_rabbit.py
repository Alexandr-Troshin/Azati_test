import json
import pika


ORDERS = [
    {'user': 'rabbit_user1', 'stock': 'Tesla', 'order_type': 'BUY',
     'shares': 10, 'price_per_share': 176},
    {'user': 'rabbit_user2', 'stock': 'Tesla', 'order_type': 'SELL',
     'shares': 5, 'price_per_share': 176}
]

credentials = pika.PlainCredentials('rabbit', 'rabbit_password')
conn_params = pika.ConnectionParameters('127.0.0.1',
                                       5672,
                                       '/',
                                       credentials)

def publish(method, body):
    properties = pika.BasicProperties(method)
    print(json.dumps(body).encode('utf-8'))
    channel.basic_publish(exchange='', routing_key='orders',
                          body=json.dumps(body).encode('utf-8'), properties=properties)
    print(properties.content_type)


if __name__ == "__main__":
    connection = pika.BlockingConnection(conn_params)
    channel = connection.channel()
    channel.queue_declare(queue='orders', durable=True)

    for _ in range(5):
        publish('put_order', ORDERS[0])
    publish('put_order', ORDERS[1])
    publish('put_order', ORDERS[1])
    publish('delete_order', ORDERS[0])
    publish('stop_consuming', {})

    connection.close()
