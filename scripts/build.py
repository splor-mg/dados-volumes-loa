from frictionless import Package, Resource
from datetime import datetime

def build_package(source_descriptor: str = 'datapackage.yaml', target_descriptor: str = 'datapackage.json'):
    
    output = Package.from_descriptor(source_descriptor)
    output.custom['updated_at'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

    for resource in output.resources:
        resource.infer(stats=True)

    output.to_json('datapackage.json')
