import os
import yaml
import logging
from kubernetes import client, config

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Load Kubernetes configuration
try:
    config.load_kube_config()
    logger.info("Kubernetes configuration loaded successfully.")
except Exception as e:
    logger.error(f"Error loading Kubernetes configuration: {e}")
    raise

namespace = "default"
v1 = client.CoreV1Api()

# Fetch all services
try:
    services = v1.list_namespaced_service(namespace)
    logger.info(f"Found {len(services.items)} services in the '{namespace}' namespace.")
except client.exceptions.ApiException as e:
    logger.error(f"Error fetching services from Kubernetes: {e}")
    raise

# Filebeat configuration with topic and partition settings
filebeat_config = {
    'filebeat.inputs': [],
    'output.kafka': {
        'hosts': ['broker1:9092', 'broker2:9092', 'broker3:9092'],
        'topic': 'service-logs',
        'codec.json': {'pretty': True},
        'bulk_max_size': 2048,
        'compression': 'gzip',
        'max_message_size': 1000000,
        'partition': 1,
        'key': '%{[fields.service]}',
    }
}

# Iterate over services and add input configurations
for service in services.items:
    service_name = service.metadata.name
    if service_name.endswith("-service"):
        filebeat_config['filebeat.inputs'].append({
            'type': 'log',
            'paths': [f'/mnt/data/logs/{service_name}/*.log'],
            'fields': {'service': service_name},
            'ignore_older': '6h'
            'close_inactive': '5m',
            'multiline': {
                'pattern': '^\d{4}-\d{2}-\d{2}',
                'negate': True,
                'match': 'before'
            }
        })
        logger.info(f"Added log input for service: {service_name}")

# Dumps configurations
filebeat_configmap = {
    'apiVersion': 'v1',
    'kind': 'ConfigMap',
    'metadata': {
        'name': 'filebeat-config',
        'namespace': namespace
    },
    'data': {
        'filebeat.yml': yaml.dump(filebeat_config)
    }
}

# Apply Configmap
try:
    k8s_client = client.ApiClient()
    v1 = client.CoreV1Api(k8s_client)
    v1.create_namespaced_config_map(namespace, filebeat_configmap)
    logger.info("Filebeat config generated and ConfigMap applied successfully.")
except client.exceptions.ApiException as e:
    logger.error(f"Error creating ConfigMap: {e}")
    raise

