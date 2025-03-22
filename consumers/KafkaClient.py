from typing import List
from kafka import KafkaAdminClient


class KafkaClient:
    def __init__(self, brokers: List[str]):
        self.brokers = brokers
        self.client = KafkaAdminClient(bootstrap_servers=self.brokers)

    def get_topics(self) -> List[str]:
        return self.client.list_topics()

    def close(self) -> None:
        self.client.close()

