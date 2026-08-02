from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM
)


MODEL_NAME = "facebook/nllb-200-1.3B"


class Command(BaseCommand):

    help = "Downloads NLLB-200 locally."


    def handle(self, *args, **kwargs):

        model_root = (
            Path(settings.BASE_DIR)
            /
            "models"
            /
            "facebook_nllb_1_3b"
        )


        model_root.mkdir(
            parents=True,
            exist_ok=True
        )


        self.stdout.write(
            f"Downloading {MODEL_NAME}"
        )


        tokenizer = AutoTokenizer.from_pretrained(
            MODEL_NAME
        )


        tokenizer.save_pretrained(
            str(model_root)
        )


        model = AutoModelForSeq2SeqLM.from_pretrained(
            MODEL_NAME
        )


        model.save_pretrained(
            str(model_root),
            safe_serialization=True
        )


        self.stdout.write(
            self.style.SUCCESS(
                f"Saved NLLB to {model_root}"
            )
        )
