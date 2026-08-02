import uuid

from django.db import models

from .choices import Status


class BaseModel(models.Model):
    """
    Abstract base model that provides common fields for all models.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TranslationRequest(BaseModel):
    """
    Stores every translation request made to the system.
    """

    source_language = models.CharField(
        max_length=20
    )

    target_language = models.CharField(
        max_length=20
    )

    source_text = models.TextField()

    translated_text = models.TextField(
        blank=True
    )

    model_name = models.CharField(
        max_length=100,
        default="facebook/nllb-200-1.3B"
    )

    adapter_name = models.CharField(
        max_length=100
    )

    adapter_version = models.CharField(
        max_length=20,
        default="1.0.0"
    )

    confidence = models.FloatField(
        null=True,
        blank=True,
        help_text="Model confidence between 0.0 and 1.0"
    )

    inference_time_ms = models.FloatField()

    input_tokens = models.PositiveIntegerField()

    output_tokens = models.PositiveIntegerField()

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.SUCCESS
    )

    error_message = models.TextField(
        blank=True
    )

    rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True
    )

    feedback = models.TextField(
        blank=True
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )

    user_agent = models.TextField(
        blank=True
    )

    session_id = models.CharField(
        max_length=128,
        blank=True
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["source_language", "target_language"]),
            models.Index(fields=["adapter_name"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return (
            f"{self.source_language} → "
            f"{self.target_language} "
            f"({self.status})"
        )
