import aio_pika
import asyncio
import os
import json

from app.database import SessionLocal
from app.models import TyreModel

RABBIT_URL = os.getenv("RABBIT_URL")
EXCHANGE = "topic_logs"

async def process_message(msg: aio_pika.IncomingMessage):
    async with msg.process():
        data = json.loads(msg.body.decode())
        print(f"[order_worker.py] Received {msg.routing_key}: {data}")

        db = SessionLocal()

        try:
            if msg.routing_key == "order.created":
                order_type = data["type"]

                for item in data["items"]:
                    tyre = db.get(TyreModel, item["tyre_id"])
                    if not tyre:
                        print("Tyre not found")
                        continue

                    if order_type == "BUY":
                        tyre.quantity += item["quantity"]
                    else:
                        tyre.quantity -= item["quantity"]

                    db.add(tyre)

                db.commit()

        except Exception as e:
            print("ERROR:", e)
            db.rollback()
        finally:
            db.close()


async def main():
    connection = await aio_pika.connect_robust(RABBIT_URL)
    channel = await connection.channel()

    exchange = await channel.declare_exchange(EXCHANGE, aio_pika.ExchangeType.TOPIC)
    queue = await channel.declare_queue("", exclusive=True)

    await queue.bind(exchange, routing_key="order.created")

    print("[order_worker.py] Listening for 'order.created'...")

    await queue.consume(process_message)

    await asyncio.Future()  # keep alive

if __name__ == "__main__":
    asyncio.run(main())
