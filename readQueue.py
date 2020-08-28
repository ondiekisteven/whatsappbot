import yaml
import asyncio
from aio_pika import connect, IncomingMessage, Message, DeliveryMode, Channel
import logging
from json import loads, dumps
from Bot import WaBot
from functools import partial


LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)

loop = asyncio.get_event_loop()


async def on_message(channel: Channel, routing_key: str, message: IncomingMessage):
    async with message.process(ignore_processed=True):
        # print(" [x] Received message %r" % message)
        msg_json = loads(message.body.decode('utf-8'))
        LOGGER.info("     Message body is: %r" % msg_json)
        bot = WaBot(msg_json)

        try:
            async def send_message(chat_id, text):
                msg = {
                    'message': text,
                    'chat_id': chat_id
                }
                _msg = Message(
                    body=dumps(msg).encode(),
                    delivery_mode=DeliveryMode.PERSISTENT
                )
                await channel.default_exchange.publish(
                    message=_msg,
                    routing_key=routing_key
                )
                LOGGER.info(f'Sent message: {chat_id} -> {text}')

            chatId = msg_json['chatId']

            reply = bot.processing()
            await send_message(chatId, reply)
            await message.ack()
        except Exception as e:
            await message.reject()
            raise e


async def main():
    with open("config.yml", "r") as ymlfile:
        cfg = yaml.load(ymlfile)

    app_name = 'steveapp'
    # Perform connection
    connection = await connect("amqp://guest:guest@3.128.231.254:5673/", loop=loop)

    # Creating a channel
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)

    # Declaring queue
    queue = await channel.declare_queue(cfg[app_name]['queue_incoming'], durable=True)

    # Start listening the queue with name 'task_queue'
    LOGGER.info(" [*] Waiting for messages. To exit press CTRL+C")
    await queue.consume(
        partial(
            on_message,
            channel,
            cfg[app_name]['queue_outgoing']
        ))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())

    # we enter a never-ending loop that waits for data and runs
    # callbacks whenever necessary.

    loop.run_forever()
