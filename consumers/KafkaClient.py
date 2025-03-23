from typing import List
from kafka import KafkaAdminClient
from env import logger
class KafkaClient:
    def __init__(self, brokers: List[str], topic: str):
        self.brokers = brokers
        self.client = KafkaAdminClient(bootstrap_servers=self.brokers)
        self.topic_name = topic

    def get_topic_partitions(self) -> List[str]:
        try:
            topics = self.get_topics()
            if topic_name in topics:
                topic_metadata = self.client.describe_topics([topic_name])
                if topic_metadata:
                    self.topic = topic_metadata[0]
                    return [partition for partition in self.topic.partition]
        except Exception as e:
            logger.error(f"Error getting topic partitions: {e}")
        finally:
            return []

    def get_topics(self) -> List[str]:
        try:
            return self.client.get_topics()
        except Exception as e:
            logger.error(f"Error getting topics: {e}")
            return []

    def close(self) -> None:
        self.client.close()

