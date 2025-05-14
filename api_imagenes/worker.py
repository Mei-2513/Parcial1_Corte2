import aio_pika
import json
from processing import process_image

async def consume():
    connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/")
    async with connection:
        channel = await connection.channel()
        
        queue = await channel.declare_queue("resize_queue", durable=True)

        await queue.consume(on_message, no_ack=False)
        
        print("Esperando mensajes...")
        await asyncio.Future()

async def on_message(message: aio_pika.IncomingMessage):
    async with message.process():
        try:
            image_data = json.loads(message.body)
            await process_image(image_data)  
            await message.ack()  
        except Exception as e:
            print(f"Error al procesar el mensaje: {e}")
            await message.nack(requeue=True)  

