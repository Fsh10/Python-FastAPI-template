import logging


class EmailConsumerService:
    def __init__(self):
        self.is_running = False
        self.total_consumers = 1
        self.consumers = []

    def start(self):
        self.is_running = True
        self.consumers.append({"id": 1, "status": "running"})
        logging.info("Email consumer started")

    def stop(self):
        self.is_running = False
        self.consumers = []
        logging.info("Email consumer stopped")

    def get_consumer_status(self):
        return {
            "is_running": self.is_running,
            "total_consumers": self.total_consumers,
            "consumers": self.consumers,
        }


email_consumer_service = EmailConsumerService()
