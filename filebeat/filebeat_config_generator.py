import os
import yaml
import logging
from kubernetes import client, config, watch

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Load Kubernetes configuration
try:
    config.load_incluster_config()
    logger.info("Kubernetes configuration loaded successfully.")
except Exception as e:
    logger.error(f"Error loading Kubernetes configuration: {e}")
    raise

namespace = "default"
v1 = client.CoreV1Api()

# Filebeat configuration with topic and partition settings
filebeat_config = {
    'filebeat.inputs': [],
    'output.kafka': {
        'hosts': ['localhost:9092'],
        'topic': 'service-logs',
        'codec.json': {'pretty': True},
        'bulk_max_size': 2048,
        'compression': 'gzip',
        'max_message_size': 1000000,
        'key': '%{[fields.service]}',
    }
}

# Generates filebeat configuration
def add_service_to_filebeat_config(service_name):
    filebeat_config['filebeat.inputs'].append({
        'type': 'log',
        'paths': [f'/mnt/data/logs/{service_name}/*.log'],
        'fields': {'service': service_name},
        'ignore_older': '6h',
        'close_inactive': '5m',
        'multiline': {
            'pattern': '^\d{4}-\d{2}-\d{2}',
            'negate': True,
            'match': 'before'
        }
    })
    logger.info(f"Added log input for service: {service_name}")

# Removes service from filebeat configuration
def remove_service_from_filebeat_config(service_name):
    filebeat_config['filebeat.inputs'] = [
        input for input in filebeat_config['filebeat.inputs'] if input['fields']['service'] != service_name
    ]
    logger.info(f"Removed log input for service: {service_name}")

#Updates ConfigMap with new filebeat configuration
def update_configmap():
    try:
        k8s_client = client.ApiClient()
        v1 = client.CoreV1Api(k8s_client)
        existing_configmap = v1.read_namespaced_config_map('filebeat-config', namespace)
        
        existing_configmap.data['filebeat.yml'] = yaml.dump(filebeat_config)
        v1.replace_namespaced_config_map('filebeat-config', namespace, existing_configmap)
        
        logger.info("Filebeat config updated successfully.")
    except client.exceptions.ApiException as e:
        logger.error(f"Error updating ConfigMap: {e}")
        raise

w = watch.Watch()
try:
    for event in w.stream(v1.list_namespaced_service, namespace=namespace):
        service_name = event['object'].metadata.name
        
        if event['type'] in ['ADDED', 'MODIFIED']:
            if service_name.endswith("-service"):
                if not any(input['fields']['service'] == service_name for input in filebeat_config['filebeat.inputs']):
                    add_service_to_filebeat_config(service_name)
                    update_configmap()

        elif event['type'] == 'DELETED':
            if service_name.endswith("-service"):
                remove_service_from_filebeat_config(service_name)
                update_configmap()

except Exception as e:
    logger.error(f"Error watching services: {e}")
