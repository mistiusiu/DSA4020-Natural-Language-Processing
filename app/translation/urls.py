from django.urls import path

from .views import (
    TranslatorPageView,
    TranslationAPIView,
    HealthAPIView,
    TranslationDirectionListView
)


urlpatterns = [
    path("", TranslatorPageView.as_view(), name="translator_page"),
    path(
        "translate/",
        TranslationAPIView.as_view(),
        name="translate"
    ),

    path(
        "translation-directions/",
        TranslationDirectionListView.as_view(),
        name="translation-directions-list",
    ),

    path(
        "health/",
        HealthAPIView.as_view(),
        name="health"
    )

]
