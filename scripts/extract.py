import logging
import subprocess

logger = logging.getLogger(__name__)

def extract_resource(resource_name: str, descriptor: str = 'datapackage.yaml'):
    logger.info(f'Extracting resource {resource_name}...')
    subprocess.run(['Rscript', 'scripts/extract.R', resource_name])
