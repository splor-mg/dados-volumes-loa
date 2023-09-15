from frictionless import Package
import petl as etl
import logging
from scripts.pipelines import transform_pipeline

logger = logging.getLogger(__name__)

def transform_resource(resource_name: str, source_descriptor: str = 'datapackage.yaml', target_descriptor: str = 'datapackage.json'):
    logger.info(f'Transforming resource {resource_name}')
    
    package = Package(source_descriptor)
    resource = package.get_resource(resource_name)
    resource.transform(transform_pipeline)
    table = resource.to_petl()
    for field in resource.schema.fields:
        if field.custom.get('target'):
            table = etl.rename(table, field.name, field.custom['target'])
    etl.tocsv(table, f'data/{resource.name}.csv', encoding='utf-8')
