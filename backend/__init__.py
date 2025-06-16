from .celery import app as celery_app  # pyright: ignore[reportUnusedImport]

__all__ = ['celery_app']
