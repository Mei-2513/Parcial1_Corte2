from fastapi import FastAPI, UploadFile, File, HTTPException
import uuid
import aio_pika
import json
import os

app = FastAPI()

IMAGES_DIR = "images"
os.makedirs(IMAGES_DIR, exist_ok=True)

status_db = {}

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Archivo no es una imagen")

    image_id = str(uuid.uuid4())
    file_path = os.path.join(IMAGES_DIR, f"{image_id}.jpg")
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    status_db[image_id] = {"estado": "subido", "procesado": []}

    connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/")
    async with connection:
        channel = await connection.channel()
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps({"id": image_id, "path": file_path}).encode()
            ),
            routing_key="resize_queue" 
        )

    return {"id": image_id, "mensaje": "Imagen recibida"}

@app.get("/status/{image_id}")
def get_status(image_id: str):
    return status_db.get(image_id, {"mensaje": "ID no encontrado"})

