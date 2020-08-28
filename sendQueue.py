import pika
import yaml


def to_queue(message):
    with open("config.yml", "r") as ymlfile:
        cfg = yaml.load(ymlfile)

    app_name = 'steveapp'

    # create connection
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='3.128.231.254', port=5673))
    channel = connection.channel()

    channel.queue_declare(queue=cfg[app_name]['queue_incoming'],
                          durable=True,)

    channel.basic_publish(
        exchange='',
        routing_key=cfg[app_name]['queue_incoming'],
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        ))
    connection.close()
    return " [x] Sent %r" % message
