import json
import uuid
from typing import Any, Dict, Optional

import aio_pika
from aio_pika.abc import AbstractChannel, AbstractConnection
from aio_pika.pool import Pool

from src.config import settings


class RabbitPublisher:
    def __init__(self, host: str, port: int, username: str, password: str, vhost: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.vhost = vhost
        self.connection: Optional[AbstractConnection] = None
        self.channel: Optional[AbstractChannel] = None
        self.connection_pool: Optional[Pool] = None
        self.channel_pool: Optional[Pool] = None

    async def connect(self):
        try:
            self.connection = await aio_pika.connect_robust(
                host=self.host,
                port=self.port,
                login=self.username,
                password=self.password,
                virtualhost=self.vhost,
            )

            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=10)

            self.connection_pool = Pool(self.get_connection, max_size=10)
            self.channel_pool = Pool(self.get_channel, max_size=10)

            await self.channel.declare_exchange(
                "main_exchange",
                aio_pika.ExchangeType.TOPIC,
                durable=True,
            )

        except Exception as e:
            raise Exception(f"Failed to connect to RabbitMQ: {str(e)}")

    async def get_connection(self) -> AbstractConnection:
        if not self.connection:
            await self.connect()
        return self.connection

    async def get_channel(self) -> AbstractChannel:
        if not self.channel:
            await self.connect()
        return self.channel

    async def publish_message(
        self, queue_name: str, message: Dict[str, Any], exclusive: bool = False
    ):
        try:
            message_body = json.dumps(message).encode()
            queue = await self.channel.declare_queue(
                name=queue_name, durable=True, exclusive=exclusive
            )
            await queue.bind("main_exchange", routing_key=queue_name)

            await self.channel.default_exchange.publish(
                aio_pika.Message(body=message_body), routing_key=queue_name
            )

        except Exception as e:
            raise Exception(
                f"Failed to publish message to queue {queue_name}: {str(e)}"
            )

    async def publish_message_and_wait(
        self, queue_name: str, message: Dict[str, Any], timeout: int = 30
    ) -> Dict[str, Any]:
        try:
            correlation_id = str(uuid.uuid4())
            response_queue = await self.channel.declare_queue(exclusive=True)

            message_body = json.dumps(message).encode()
            await self.channel.default_exchange.publish(
                aio_pika.Message(
                    body=message_body,
                    correlation_id=correlation_id,
                    reply_to=response_queue.name,
                ),
                routing_key=queue_name,
            )

            try:
                async with response_queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        if message.correlation_id == correlation_id:
                            return json.loads(message.body.decode())
            except Exception as e:
                raise Exception(f"Error processing response: {str(e)}")

        except Exception as e:
            raise Exception(f"Error in publish_message_and_wait: {str(e)}")

    async def check_activation_key(self, activation_key_id: str) -> Dict[str, Any]:
        try:
            message = {
                "action": "check_activation_key",
                "activation_key_id": activation_key_id,
            }
            return await self.publish_message_and_wait("activation_keys", message)
        except Exception as e:
            raise Exception(f"Error checking activation key: {str(e)}")

    async def activate_key(
        self, activation_key_id: str, organization_name: str
    ) -> Dict[str, Any]:
        try:
            message = {
                "action": "activate_key",
                "activation_key_id": activation_key_id,
                "organization_name": organization_name,
            }
            return await self.publish_message_and_wait("activation_keys", message)
        except Exception as e:
            raise Exception(f"Error activating key: {str(e)}")

    async def disconnect(self):
        try:
            if self.channel:
                await self.channel.close()
            if self.connection:
                await self.connection.close()
        except Exception as e:
            raise Exception(f"Error during disconnect: {str(e)}")


publisher = RabbitPublisher(
    host=settings.RABBITMQ_HOST,
    port=settings.RABBITMQ_PORT,
    username=settings.RABBITMQ_USER,
    password=settings.RABBITMQ_PASSWORD,
    vhost=settings.RABBITMQ_HOST,
)
