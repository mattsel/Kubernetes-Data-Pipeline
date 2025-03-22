import threading
from typing import List
from KafkaClient import KafkaClient


def main(brokers: List[str], batch: int, threads: int) -> None:
    kafka_client = KafkaClient(brokers)
    topics = kafka_client.get_topics()


