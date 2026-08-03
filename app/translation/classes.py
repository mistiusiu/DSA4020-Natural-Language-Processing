import torch
import time

from pathlib import Path
from threading import Lock
from typing import Tuple, List, Optional

from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    PreTrainedTokenizer
)

from peft import (
    PeftModel
)

from dataclasses import dataclass

from config.constants import (
    BASE_MODEL_DIRECTORY,
    DEVICE,
    TORCH_DTYPE,
    MAX_GENERATION_LENGTH
)

from config.enums import (
    TranslationDirection
)


@dataclass
class TranslationComponents:
    tokenizer: object
    model: object


class ModelRegistry:
    """
    Singleton registry for NLLB-200.

    Loads:

        • Tokenizer once
        • Base model once
        • Six LoRA adapters once

    Requests simply switch adapters.

    Thread-safe.
    """

    _instance = None

    _lock = Lock()


    def __new__(cls):

        if cls._instance is None:
            with cls._lock:

                if cls._instance is None:

                    cls._instance = super().__new__(cls)

        return cls._instance


    def __init__(self):

        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self.tokenizer = None
        self.model = None
        self.loaded = False


    def load(self):

        """
        Load tokenizer, base model and all adapters.

        Safe to call multiple times.
        """

        with self._lock:

            if self.loaded:
                return

            self._load_tokenizer()
            self._load_base_model()
            self._load_all_adapters()
            self.loaded = True

    def _load_tokenizer(self):
        self.tokenizer = AutoTokenizer.from_pretrained(
            BASE_MODEL_DIRECTORY
        )


    def _load_base_model(self):

        dtype = (
            torch.float16
            if TORCH_DTYPE == "float16"
            else torch.float32
        )


        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            BASE_MODEL_DIRECTORY,
            torch_dtype=dtype,
            device_map=DEVICE,
            low_cpu_mem_usage=True

        )
        self.model.eval()

    def _load_all_adapters(self):

        """
        Loads all adapters into the base model.
        """

        first = True

        for direction in TranslationDirection:
            adapter_path = (
                Path(
                    direction.adapter_directory
                )
            )

            if first:
                self.model = PeftModel.from_pretrained(
                    self.model,
                    adapter_path,
                    adapter_name=
                        direction.adapter_name
                )
                first = False
                continue

            self.model.load_adapter(
                model_id=str(adapter_path),
                adapter_name=
                    direction.adapter_name
            )


        self.model.set_adapter(
            TranslationDirection
            .ENG_TO_SWH
            .adapter_name
        )


    def get_tokenizer(self):
        self.load()

        return self.tokenizer


    def get_model(
        self,
        direction: TranslationDirection
    ):

        """
        Activate adapter.

        Returns the same cached model.
        """

        self.load()
        self.model.set_adapter(
            direction.adapter_name
        )

        return self.model


    def get_components(
        self,
        direction: TranslationDirection
    ) -> TranslationComponents:

        return TranslationComponents(
            tokenizer=self.get_tokenizer(),
            model=self.get_model(direction)
        )

    def list_loaded_adapters(self):
        self.load()

        return self.model.peft_config.keys()

    def unload(self):

        """
        Useful for tests.
        """
        self.model = None
        self.tokenizer = None
        self.loaded = False


@dataclass
class TranslationResult:
    """
    Output from a translation request.
    """

    source_text: str

    translated_text: str

    source_language: str

    target_language: str

    adapter_name: str

    confidence: float

    inference_time_ms: float

    input_tokens: int

    output_tokens: int


class TranslationInferenceService:
    """
    Handles NLLB inference.

    Does not load models.

    Delegates model management to ModelRegistry.
    """

    def __init__(self):

        self.registry = ModelRegistry()

    def _calculate_confidence(
        self,
        scores
    ) -> float:


        if not scores:

            return 0.0


        probabilities = []


        for step_scores in scores:


            token_probabilities = (
                torch.softmax(
                    step_scores,
                    dim=-1
                )
            )


            max_probability = (
                token_probabilities
                .max()
                .item()
            )


            probabilities.append(
                max_probability
            )


        confidence = sum(
            probabilities
        ) / len(probabilities)


        return round(
            confidence,
            4
        )

    def translate(
        self,
        text: str,
        direction: TranslationDirection
    ) -> TranslationResult:


        components = (
            self.registry.get_components(
                direction
            )
        )

        tokenizer = components.tokenizer
        model = components.model


        start_time = time.perf_counter()


        #
        # Configure tokenizer
        #

        tokenizer.src_lang = (
            direction.source.code
        )


        #
        # Tokenize
        #

        inputs = tokenizer(

            text,

            return_tensors="pt",

            truncation=True,

            padding=True

        )


        input_tokens = (
            inputs.input_ids.shape[1]
        )


        inputs = {
            key: value.to(
                model.device
            )

            for key, value
            in inputs.items()
        }


        #
        # Generate translation
        #

        with torch.no_grad():

            outputs = model.generate(

                **inputs,

                forced_bos_token_id = (
                    tokenizer.convert_tokens_to_ids(
                        TranslationDirection
                        .ENG_TO_SWH
                        .target
                        .code
                    )
                ),

                max_length=
                    MAX_GENERATION_LENGTH,

                num_beams=4,

                return_dict_in_generate=True,

                output_scores=True

            )


        #
        # Decode
        #

        translated = tokenizer.batch_decode(

            outputs.sequences,

            skip_special_tokens=True

        )[0]


        output_tokens = (
            outputs.sequences.shape[1]
        )


        #
        # Confidence
        #

        confidence = (
            self._calculate_confidence(
                outputs.scores
            )
        )


        elapsed = (
            time.perf_counter()
            -
            start_time
        )


        return TranslationResult(

            source_text=text,

            translated_text=translated,

            source_language=
                direction.source.code,

            target_language=
                direction.target.code,

            adapter_name=
                direction.adapter_name,

            confidence=confidence,

            inference_time_ms=
                elapsed * 1000,

            input_tokens=input_tokens,

            output_tokens=output_tokens

        )

    def translate_batch(
        self,
        texts: List[str],
        direction: TranslationDirection

    ) -> List[TranslationResult]:


        results = []


        for text in texts:

            result = self.translate(

                text,

                direction

            )


            results.append(
                result
            )


        return results
