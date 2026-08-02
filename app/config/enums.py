from enum import Enum
from pathlib import Path

from .constants import ADAPTER_DIRECTORY


class Language(Enum):

    ENGLISH = (
        "eng_Latn",
        "English"
    )

    SWAHILI = (
        "swh_Latn",
        "Swahili"
    )

    GIKUYU = (
        "kik_Latn",
        "Gikuyu"
    )


    @property
    def code(self):

        return self.value[0]


    @property
    def display_name(self):

        return self.value[1]


class TranslationDirection(Enum):

    ENG_TO_SWH = (

        Language.ENGLISH,

        Language.SWAHILI,

        "eng_to_swh"

    )

    SWH_TO_ENG = (

        Language.SWAHILI,

        Language.ENGLISH,

        "swh_to_eng"

    )

    ENG_TO_GIK = (

        Language.ENGLISH,

        Language.GIKUYU,

        "eng_to_gik"

    )

    GIK_TO_ENG = (

        Language.GIKUYU,

        Language.ENGLISH,

        "gik_to_eng"

    )

    SWH_TO_GIK = (

        Language.SWAHILI,

        Language.GIKUYU,

        "swh_to_gik"

    )

    GIK_TO_SWH = (

        Language.GIKUYU,

        Language.SWAHILI,

        "gik_to_swh"

    )

    @property
    def source(self):

        return self.value[0]


    @property
    def target(self):

        return self.value[1]


    @property
    def adapter_name(self):

        return self.value[2]


    @property
    def adapter_directory(self) -> Path:

        return (
            ADAPTER_DIRECTORY /
            self.adapter_name
        )


    @classmethod
    def from_languages(
        cls,
        source: Language,
        target: Language
    ):
        for direction in cls:

            if (
                direction.source == source
                and
                direction.target == target
            ):
                return direction


        raise ValueError(
            f"{source.name} -> {target.name} is unsupported."
        )

    @classmethod
    def from_codes(
        cls,
        source_code: str,
        target_code: str
    ):
        for direction in cls:
            if (

                direction.source.code == source_code
                and
                direction.target.code == target_code
            ):
                return direction

        raise ValueError(
            "Unsupported translation direction."
        )
