# tyres_service/app/tyre_rpc_worker.py
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
        print(f"[tyre_rpc_worker] Received {msg.routing_key}: {data}")

        db = SessionLocal()
        try:
            tyre_id = data.get("tyre_id")
            tyre = db.get(TyreModel, tyre_id)

            if not tyre:
                response = {"ok": False}
            else:
                response = {
                    "ok": True,
                    "tyre": {
                        "id": tyre.id,
                        "brand": tyre.brand,
                        "model": tyre.model,
                        "size": tyre.size,
                        "supplier": tyre.supplier,
                        "retail_cost": str(tyre.retail_cost),
                        "quantity": tyre.quantity
                    }
                }

        except Exception as e:
            print("ERROR:", e)
            response = {"ok": False}
        finally:
            db.close()

        if msg.reply_to and msg.correlation_id:
            await msg.channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(response).encode(),
                    correlation_id=msg.correlation_id
                ),
                routing_key=msg.reply_to
            )

async def main():
    connection = await aio_pika.connect_robust(RABBIT_URL)
    channel = await connection.channel()

    exchange = await channel.declare_exchange(EXCHANGE, aio_pika.ExchangeType.TOPIC)
    queue = await channel.declare_queue("rpc.tyres.get", durable=True)

    await queue.bind(exchange, routing_key="tyres.get")

    print("[tyre_rpc_worker] Listening for tyres.get")

    await queue.consume(process_message)
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
