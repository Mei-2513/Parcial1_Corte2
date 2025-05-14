# Procesamiento de Imágenes con FastAPI, RabbitMQ y Docker

Este proyecto fue desarrollado como parte del parcial. Consiste en un sistema que recibe imágenes desde una API hecha en FastAPI, las envía a un *worker* para que las procese (redimensionar + marca de agua), y usa RabbitMQ para comunicar todos los componentes. Todo está montado con Docker.

---

## Componentes del Sistema

- **API**: Recibe imágenes y las publica en una cola de RabbitMQ.
- **Worker**: Toma los mensajes de la cola y procesa las imágenes.
- **RabbitMQ**: Gestiona los mensajes entre la API y el worker.

Todo se levanta fácilmente con `docker-compose`.

---

## Arquitectura y Decisiones Técnicas

###  ¿Por qué un solo *worker*?

Para esta versión usamos 1 `worker` por simplicidad, pero si hay muchas imágenes o usuarios concurrentes, se pueden levantar más réplicas y RabbitMQ se encarga de repartir la carga automáticamente.

### Tipo de Exchange y su Escalabilidad

Usamos un **exchange tipo `fanout`** para notificar cuando se ha procesado una imagen:

- Fanout manda el mensaje a todas las colas conectadas.
- Nos sirve porque todos los `workers` hacen la misma tarea.
- Si se agregan más `workers`, automáticamente podrán recibir mensajes sin cambiar el código.

### Manejo de Errores y Reintentos

- Si una imagen no se puede procesar, el `worker` lanza un error y RabbitMQ reintenta el mensaje.
- Si falla muchas veces, se puede configurar un **Dead Letter Exchange** (no implementado aquí, pero es posible) para enviar esos mensajes a otra cola especial.
- En la API se valida que el archivo subido sea una imagen.

---

## Optimización y Escalabilidad

- **Docker Compose** simplifica todo. Con un solo comando (`docker-compose up`) levantamos la API, el worker y RabbitMQ.
- Se puede **escalar horizontalmente** duplicando `workers` en Compose (`deploy.replicas`).
- RabbitMQ permite manejar cargas grandes y desacopla los componentes.
- El sistema está listo para agregar mejoras como procesamiento paralelo o nuevos tipos de tareas.

---

## Cómo Ejecutar

1. Clona el repositorio:

    ```bash
    git clone https://github.com/Mei-2513/Parcial1_Corte2.git
    cd tu-repo
    ```

2. Construye y levanta todo:

    ```bash
    docker-compose up --build
    ```

3. Abre la API en:  
    [http://localhost:8000/docs](http://localhost:8000/docs)  
    y prueba subiendo una imagen desde el endpoint `/upload`. las imagenes se estan guardando en Parcial1/app/api_imagenes/images

---

## Cola y Exchange usados

- **Cola principal**: `resize_queue`
- **Exchange de notificación**: `processed_exchange` (tipo `fanout`)

