from typing import List
from env import logger

class Consumer:
    def __init__(self, topic: str, brokers: List[str], partition: int):
        self.consumer_client = None
        self.topic = topic
        self.brokers = brokers
        self.partition = partition

    def get_consumer_client(self) -> KafkaConsumer:
        try:
            consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=self.brokers,
                auto_offset_reset='earliest',
                enable_auto_commit=False,
                group_id=None
            )
            consumer.assign([TopicPartition(self.topic, self.partition)])
            self.consumer_client = consumer
            return self.consumer_client
        except Exception as e:
            logger.error(f"Error creating consumer: {e}")
            return None
    
    def close(self) -> None:
        self.consumer_client.close()

