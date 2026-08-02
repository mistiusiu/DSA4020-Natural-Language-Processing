from django.urls import path

from .views import (
    TranslationAPIView,
    HealthAPIView
)


urlpatterns = [

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
