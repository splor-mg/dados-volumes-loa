from frictionless import Package
import typer
from typing_extensions import Annotated
import logging
from scripts.extract import extract_resource
from scripts.build import build_package

app = typer.Typer(pretty_exceptions_show_locals=False)

@app.callback()
def callback():
    """
    ETL scripts.
    """

@app.command()
def resources(descriptor: str = 'datapackage.yaml', path: Annotated[bool, typer.Option(help="Return resource path")] = False):
    """
    Data package resource names
    """
    package = Package(descriptor)
    if path:
        output = [resource.path for resource in package.resources]
    else:
        output = package.resource_names
    print(' '.join(output))
    return 0

app.command(name="extract")(extract_resource)
app.command(name="build")(build_package)

if __name__ == "__main__":
    LOG_FORMAT = '%(asctime)s %(levelname)-5.5s [%(name)s] %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
    logging.basicConfig(format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT, level=logging.INFO)
    app()
