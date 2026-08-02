from django.core.management.base import BaseCommand

from translation.classes import (
    ModelRegistry
)

from config.enums import (
    TranslationDirection
)


class Command(BaseCommand):

    help = (
        "Loads NLLB-200 and LoRA adapters "
        "and performs a warmup inference."
    )


    def handle(self, *args, **options):

        self.stdout.write(
            "Loading translation model..."
        )


        registry = ModelRegistry()

        registry.load()


        self.stdout.write(
            "Model loaded."
        )


        self.stdout.write(
            "Loaded adapters:"
        )


        for adapter in (
            registry.list_loaded_adapters()
        ):

            self.stdout.write(
                f" - {adapter}"
            )


        self.stdout.write(
            "Running warmup inference..."
        )


        components = registry.get_components(
            TranslationDirection.ENG_TO_SWH
        )

        tokenizer = components.tokenizer
        model = components.model


        tokenizer.src_lang = (
            TranslationDirection
            .ENG_TO_SWH
            .source
            .code
        )


        inputs = tokenizer(

            "The vaccination campaign starts tomorrow.",

            return_tensors="pt"

        )


        inputs = {

            key: value.to(model.device)

            for key, value in inputs.items()

        }


        model.generate(

            **inputs,

            forced_bos_token_id = (
                tokenizer.convert_tokens_to_ids(
                    TranslationDirection
                    .ENG_TO_SWH
                    .target
                    .code
                )
            ),

            max_length=64

        )


        self.stdout.write(
            self.style.SUCCESS(
                "Model warmup completed successfully."
            )
        )
