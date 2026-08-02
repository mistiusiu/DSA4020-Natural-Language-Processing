from django.apps import AppConfig


class TranslationConfig(AppConfig):
    name = 'translation'


    def ready(self):

        from translation.classes import (
            ModelRegistry
        )

        registry = ModelRegistry()

        registry.load()
