import asyncio
import json
import uuid
from typing import Callable, List

from aio_pika import Message, connect_robust
from aio_pika.abc import (
    AbstractChannel,
    AbstractConnection,
    AbstractExchange,
)

from src.config import settings


class RabbitConnection:
    _connection: AbstractConnection | None = None
    _channel: AbstractChannel | None = None
    _publish_channel: AbstractChannel | None = None
    _exchange: AbstractExchange | None = None
    _active_consumers: dict = {}

    async def connect(self) -> None:
        try:
            host = settings.RABBITMQ_HOST

            self._connection = await connect_robust(
                host=host,
                port=settings.RABBITMQ_PORT,
                login=settings.RABBITMQ_USER,
                password=settings.RABBITMQ_PASSWORD,
                timeout=30,
                reconnect_interval=5,
                ssl=settings.RABBITMQ_SSL,
            )

            if not self._connection:
                raise ConnectionError("Connection object is None after connect_robust")

            self._channel = await self._connection.channel(publisher_confirms=False)
            if not self._channel:
                raise ConnectionError("Channel object is None after creation")

            self._exchange = await self._channel.declare_exchange(
                "details",
                durable=True,
            )
            if not self._exchange:
                raise ConnectionError("Exchange object is None after creation")

        except Exception as e:
            await self.disconnect()
            raise ConnectionError(
                f"Failed to establish connection with RabbitMQ: {str(e)}"
            )

    async def disconnect(self) -> None:
        try:
            if self._publish_channel and not self._publish_channel.is_closed:
                await self._publish_channel.close()

            if self._channel and not self._channel.is_closed:
                await self._channel.close()

            if self._connection and not self._connection.is_closed:
                await self._connection.close()

        except Exception as e:
            pass

    async def send_messages(
        self, messages: List[str], routing_key: str, delay: int = None
    ):
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                if not self._connection or self._connection.is_closed:
                    await self.connect()

                if not self._publish_channel or self._publish_channel.is_closed:
                    self._publish_channel = await self._connection.channel(
                        publisher_confirms=False
                    )

                publish_exchange = await self._publish_channel.declare_exchange(
                    "details", durable=True
                )

                queue = await self._publish_channel.declare_queue(
                    name=routing_key, durable=True
                )
                await queue.bind(publish_exchange, routing_key=routing_key)

                try:
                    async with self._publish_channel.transaction():
                        headers = None
                        if delay:
                            headers = {"x-delay": f"{delay * 1000}"}

                        for message in messages:
                            try:
                                msg_dict = json.loads(message)
                                message = json.dumps(msg_dict)
                            except Exception:
                                pass
                            message_id = str(uuid.uuid4())
                            msg_obj = Message(
                                body=message.encode(),
                                headers=headers,
                                message_id=message_id,
                            )
                            await publish_exchange.publish(
                                message=msg_obj,
                                routing_key=routing_key,
                            )

                    break

                except Exception as tx_error:
                    headers = None
                    if delay:
                        headers = {"x-delay": f"{delay * 1000}"}

                    for message in messages:
                        try:
                            msg_dict = json.loads(message)

                            message = json.dumps(msg_dict)
                        except Exception:
                            pass
                        message_id = str(uuid.uuid4())
                        msg_obj = Message(
                            body=message.encode(),
                            headers=headers,
                            message_id=message_id,
                        )
                        await publish_exchange.publish(
                            message=msg_obj,
                            routing_key=routing_key,
                        )
                    break

            except Exception as e:
                retry_count += 1
                await self.disconnect()

                if retry_count >= max_retries:
                    raise
                else:
                    await asyncio.sleep(2**retry_count)

    async def get_messages(
        self, callback: Callable, routing_key: str, prefetch_count: int = None
    ):
        if routing_key in self._active_consumers:
            return

        async def consumer_loop():
            try:
                if not self._connection or self._connection.is_closed:
                    await self.connect()
                    if not self._connection:
                        raise ConnectionError(
                            "Failed to establish connection with RabbitMQ"
                        )

                if not self._channel or self._channel.is_closed:
                    self._channel = await self._connection.channel(
                        publisher_confirms=False
                    )
                    if not self._channel:
                        raise ConnectionError("Failed to create channel")

                queue = await self._channel.declare_queue(
                    name=routing_key, durable=True
                )
                await queue.bind(self._exchange, routing_key=routing_key)

                if prefetch_count:
                    await self._channel.set_qos(prefetch_count=prefetch_count)

                async def wrapped_callback(message):
                    message_acked = False
                    try:
                        message_id = getattr(message, "message_id", None) or str(
                            uuid.uuid4()
                        )
                        try:
                            payload = message.body.decode()
                        except Exception:
                            payload = str(message.body)

                        await callback(message)

                    except Exception as e:
                        pass

                await queue.consume(wrapped_callback)

            except Exception as e:
                await asyncio.sleep(5)

        task = asyncio.create_task(consumer_loop())
        self._active_consumers[routing_key] = task


rabbit_connection = RabbitConnection()
