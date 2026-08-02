import torch

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


from .serializers import (
    TranslationSerializer,
    TranslationResponseSerializer
)


from .classes import (
    TranslationInferenceService,
    ModelRegistry
)


from .models import (
    TranslationRequest
)


class HealthAPIView(APIView):
    """
    Service health check.

    Checks:
    - Application availability
    - Model loading status
    - GPU availability
    - Loaded adapters
    """


    def get(self, request):

        registry = ModelRegistry()


        try:

            model_loaded = (
                registry.loaded
                and
                registry.model is not None
            )


            adapters = []

            if model_loaded:

                adapters = list(
                    registry
                    .list_loaded_adapters()
                )


            return Response(
                {
                    "status": "healthy",

                    "model_loaded":
                        model_loaded,

                    "model":
                        "facebook/nllb-200-1.3B",

                    "device":
                        str(
                            registry.model.device
                        )
                        if model_loaded
                        else None,

                    "cuda_available":
                        torch.cuda.is_available(),

                    "gpu":
                        torch.cuda.get_device_name(0)
                        if torch.cuda.is_available()
                        else None,

                    "adapters":
                        adapters
                }
            )


        except Exception as error:

            return Response(
                {
                    "status": "unhealthy",

                    "error":
                        str(error)
                },
                status=503
            )


class TranslationAPIView(APIView):
    def post(
        self,
        request
    ):

        serializer = TranslationSerializer(
            data=request.data
        )


        serializer.is_valid(
            raise_exception=True
        )


        data = serializer.validated_data


        service = (
            TranslationInferenceService()
        )


        try:

            result = service.translate(

                text=
                data["source_text"],

                direction=
                data["direction"]

            )


            TranslationRequest.objects.create(

                source_language=
                    result.source_language,

                target_language=
                    result.target_language,

                source_text=
                    result.source_text,

                translated_text=
                    result.translated_text,

                model_name=
                    "facebook/nllb-200-1.3B",

                adapter_name=
                    result.adapter_name,

                confidence=
                    result.confidence,

                inference_time_ms=
                    result.inference_time_ms,

                input_tokens=
                    result.input_tokens,

                output_tokens=
                    result.output_tokens,

                status=
                    "SUCCESS"

            )


            response = (
                TranslationResponseSerializer(
                    {
                        "translated_text":
                            result.translated_text,
                        "confidence":
                            result.confidence,
                        "inference_time_ms":
                            result.inference_time_ms,
                        "adapter_name":
                            result.adapter_name,
                        "source_language":
                            result.source_language,
                        "target_language":
                            result.target_language
                    }
                )
            )


            return Response(
                response.data,
                status=status.HTTP_200_OK
            )


        except Exception as error:

            TranslationRequest.objects.create(
                source_language=
                    data["source_language"],
                target_language=
                    data["target_language"],
                source_text=
                    data["source_text"],
                status=
                    "FAILED",
                error_message=
                    str(error)
            )


            return Response(
                {
                    "error":
                    str(error)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR

            )
