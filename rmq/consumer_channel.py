import asyncio

from aio_pika import ExchangeType, connect
from aio_pika.abc import AbstractIncomingMessage


async def on_message(message: AbstractIncomingMessage) -> None:
    async with message.process():
        print(f"[x] {message.body!r}")


async def main() -> None:
    # Perform connection
    connection = await connect("amqp://user:user@localhost/")

    async with connection:
        # Creating a channel
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)

        logs_exchange = await channel.declare_exchange(
            "yrmq.demo-xchange", ExchangeType.DIRECT,
        )

        # Declaring queue
        queue = await channel.declare_queue(exclusive=False)

        # Binding the queue to the exchange
        await queue.bind(logs_exchange,routing_key='info')

        # Start listening the queue
        await queue.consume(on_message)

        print(" [*] Waiting for logs. To exit press CTRL+C")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())