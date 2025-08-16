# Third Party Imports
from config.celery_app import app as celery_app

# Exports
__all__: list[str] = ["celery_app"]
