from rest_framework import serializers

from config.enums import (
    TranslationDirection
)


class LanguageSerializer(serializers.Serializer):
    """
    Serializes individual Language enum/object attributes.
    """
    name = serializers.CharField()
    code = serializers.CharField()


class TranslationDirectionSerializer(serializers.Serializer):
    """
    Serializes TranslationDirection Enum instances.
    """
    id = serializers.CharField(source="name")  # e.g., 'ENG_TO_SWH'
    adapter_name = serializers.CharField()
    source = LanguageSerializer()
    target = LanguageSerializer()


class TranslationSerializer(
    serializers.Serializer
):

    source_text = serializers.CharField(
        required=True
    )


    source_language = serializers.CharField(
        required=True
    )


    target_language = serializers.CharField(
        required=True
    )


    def validate(self, data):

        try:

            direction = (
                TranslationDirection
                .from_codes(
                    data["source_language"],
                    data["target_language"]
                )
            )

            data["direction"] = direction


        except ValueError as error:

            raise serializers.ValidationError(
                str(error)
            )


        return data


class TranslationResponseSerializer(
    serializers.Serializer
):

    translated_text = serializers.CharField()

    confidence = serializers.FloatField()

    inference_time_ms = serializers.FloatField()

    adapter_name = serializers.CharField()

    source_language = serializers.CharField()

    target_language = serializers.CharField()
