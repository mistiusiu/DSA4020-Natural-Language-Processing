from django.urls import path

from .views import (
    TranslatorPageView,
    TranslationAPIView,
    HealthAPIView
)


urlpatterns = [
    path("", TranslatorPageView.as_view(), name="translator_page"),
    path(
        "translate/",
        TranslationAPIView.as_view(),
        name="translate"
    ),

    path(
        "health/",
        HealthAPIView.as_view(),
        name="health"
    )

]
