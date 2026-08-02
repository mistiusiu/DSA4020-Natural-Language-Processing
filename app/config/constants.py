from pathlib import Path

from django.conf import settings


#
# Base Model
#

NLLB_MODEL_NAME = "facebook/nllb-200-1.3B"


#
# Local Storage
#

MODEL_ROOT = (
    Path(settings.BASE_DIR)
    / "models"
)

BASE_MODEL_DIRECTORY = (
    MODEL_ROOT
    / "facebook_nllb_1_3b"
)

ADAPTER_DIRECTORY = (
    MODEL_ROOT
    / "adapters"
)


#
# Translation
#

MAX_GENERATION_LENGTH = 256

DEFAULT_BEAM_SIZE = 4

DEFAULT_TEMPERATURE = 1.0

DEFAULT_TOP_P = 1.0


#
# Runtime
#

DEVICE = "cuda"

TORCH_DTYPE = "float16"
