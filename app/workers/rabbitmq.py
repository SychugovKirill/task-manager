import aio_pika, asyncio

connection: aio_pika.RobustConnection = None
channel: aio_pika.Channel = None
queue: aio_pika.Queue = None


async def init_rabbitmq():
    global connection, channel, queue

    if connection:
        return

    for attempt in range(10):
        try:
            print(f"Подключение к RabbitMQ (попытка {attempt + 1}/10)...")
            connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq:5672/")
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=5)

            queue = await channel.declare_queue("task_queue", durable=True, arguments={"x-max-priority": 10})

            print("RabbitMQ коннект установлен.")
            return

        except Exception as e:
            print(f"Failed to connect to RabbitMQ: {e}")
            await asyncio.sleep(3)

    raise RuntimeError("Не удалось подключиться с 10-ти попыток")


async def get_channel() -> aio_pika.Channel:
    return channel


async def get_connection() -> aio_pika.RobustConnection:
    return connection


async def get_queue() -> aio_pika.Queue:
    return queue


async def close_rabbitmq():
    if connection:
        await connection.close()
