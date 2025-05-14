import os
from PIL import Image, ImageDraw, ImageFont
import aio_pika

PROCESSED_IMAGES_DIR = "processed_images"
os.makedirs(PROCESSED_IMAGES_DIR, exist_ok=True)

async def process_image(image_data):
    image_id = image_data['id']
    file_path = image_data['path']
    print(f"Procesando la imagen {image_id} en {file_path}")

    try:
        img = Image.open(file_path)
        img = img.resize((800, 800)) 
        processed_file_path = os.path.join(PROCESSED_IMAGES_DIR, f"{image_id}_processed.jpg")
        img.save(processed_file_path)  

        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        text = "Marca de agua"
        draw.text((10, 10), text, fill="white", font=font)
        img.save(processed_file_path)

        print(f"Imagen procesada: {image_id} guardada en {processed_file_path}")
        await publish_processed_event(image_id)

    except Exception as e:
        print(f"Error en el procesamiento de la imagen {image_id}: {e}")
        raise

async def publish_processed_event(image_id):
    connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/")
    async with connection:
        channel = await connection.channel()
        exchange = await channel.declare_exchange('processed_images', aio_pika.ExchangeType.FANOUT)
        message = aio_pika.Message(body=f"Imagen {image_id} procesada".encode())
        await exchange.publish(message, routing_key="")  

