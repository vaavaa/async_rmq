import asyncio
from contextlib import asynccontextmanager

import aio_pika
from async_timeout import timeout


async def consume_test_rmq(loop):
    # Connecting with the given parameters is also possible.
    # aio_pika.connect_robust(host="host", login="login", password="password")
    # You can only choose one option to create a connection, url or kw-based params.
    connection = await aio_pika.connect_robust(
        "amqp://user:user@127.0.0.1/", loop=loop
    )

    async with connection:
        queue_name = "test_queue"

        # Creating channel
        channel: aio_pika.abc.AbstractChannel = await connection.channel()

        # Declaring queue
        queue: aio_pika.abc.AbstractQueue = await channel.declare_queue(
            queue_name,
            auto_delete=True
        )

        async with queue.iterator() as queue_iter:
            # Cancel consuming after __aexit__
            async for message in queue_iter:
                async with message.process():
                    print(message.body)

                    if queue.name in message.body.decode():
                        break


@asynccontextmanager
async def my_acm(test_loop):
    print('before')
    await consume_test_rmq(test_loop)
    yield
    print('after')


@asynccontextmanager
async def my_acm_plus_timeout(time, test_loop):
    async with timeout(time):
        async with my_acm(test_loop):
            yield


async def main():
    test_loop = asyncio.get_event_loop()
    while 1:
        async with my_acm_plus_timeout(400, test_loop):
            await asyncio.sleep(1.5)

    # try:


asyncio.run(main())
# except asyncio.CancelledError:
#     raise
# except Exception:
#     print('an error has occurred')
