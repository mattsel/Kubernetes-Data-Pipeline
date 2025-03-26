import os
from typing import Dict
import json
from elasticsearch import Elasticsearch
from env import logger

class Elk:
    def __init__(self):
        host = os.getenv('ELK_HOST', 'localhost')
        port = os.getenv('ELK_PORT', '9200')
        user = os.getenv('ELK_USER')
        password = os.getenv('ELK_PASS')
        try:
            if user and password:
                logger.info("ELK credentials provided")
                self.client = Elasticsearch(
                    [f'http://{host}:{port}'],
                    basic_auth=(user, password)
                )
            else:
                logger.info("No ELK credentials provided")
                self.client = Elasticsearch([f'http://{host}:{port}'])
        except Exception as e:
            logger.error(f"Error connecting to ELK: {e}")

    # Converts message to dictionary, ensuring it is a valid JSON
    def to_dict(self, message: Dict[str, str]) -> Dict[str, str]:
        try:
            data = json.loads(message)
            service = data.get("service")
            level = data.get("level")
            timestamp = data.get("timestamp")
            hostname = data.get("hostname")
            message = data.get("message")
            return {
                "service": service,
                "level": level,
                "@timestamp": timestamp,
                "hostname": hostname,
                "message": message
            }
        except json.JSONDecodeError:
            logger.error("Error decoding message")
            return None
    
    # Posts message to ELK
    def post_to_elk(self, index: str, document: dict):
        try:
            response = self.client.index(index=index, document=document)
            logger.info(f"Message posted to ELK: {response}")
        except Exception as e:
            logger.info(f"Error posting message to ELK: {e}")
