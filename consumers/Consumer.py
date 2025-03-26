from typing import List
from env import logger
from kafka import KafkaConsumer, TopicPartition

class Consumer:
    def __init__(self, topic: str, brokers: List[str], batch: int) -> None:
        self.topic = topic
        self.brokers = brokers
        self.batch = batch
        self.client = KafkaConsumer(
            bootstrap_servers=self.brokers,
            auto_offset_reset='earliest',
            enable_auto_commit=False,
            group_id='console-consumer-64406',
        )

    # Generates consumer client to consume messages from a partition
    def assign_topic_partition(self, partition: int) -> KafkaConsumer:
        try:
            self.client.assign([TopicPartition(self.topic, partition)])
            return self.client
        except Exception as e:
            logger.error(f"Error creating consumer: {e}")
            return None
    
    def get_topic_partitions(self) -> List[int]:
        try:
            return self.client.partitions_for_topic(self.topic)
        except Exception as e:
            logger.error(f"Error getting topic partitions: {e}")
            return None

    # Gracefully closes the consumer client
    def close(self) -> None:
        self.client.close()

