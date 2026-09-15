import uuid
import secrets
import string

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


def generate_passkey():
    characters = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(characters) for _ in range(8))


class Transaction(models.Model):
    class Requirements(models.TextChoices):
        COMPLETE = "complete", "Complete and accepted"
        INCOMPLETE = "incomplete", "Incomplete"

    class Priority(models.TextChoices):
        REGULAR = "regular", "Regular"
        PRIORITY = "priority", "Priority client"
        URGENT = "validated_urgent", "Validated urgent"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    tracking_id = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        editable=False,
        null=True,
    )

    passkey = models.CharField(
        max_length=12,
        unique=True,
        db_index=True,
        editable=False,
        null=True,
        blank=True,
    )

    ebqs_number = models.CharField(
        max_length=40,
        db_index=True
    )

    category = models.CharField(
        max_length=120,
        db_index=True
    )

    requirements_status = models.CharField(
        max_length=20,
        choices=Requirements.choices
    )

    priority_category = models.CharField(
        max_length=30,
        choices=Priority.choices,
        default=Priority.REGULAR
    )

    received_at = models.DateTimeField()

    accepted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    threshold_minutes = models.PositiveIntegerField(
        help_text="Approved category threshold in minutes"
    )

    current_stage = models.CharField(
        max_length=40,
        default="received"
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    adjusted_duration_minutes = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    final_label = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ("on_time", "On time"),
            ("delayed", "Delayed")
        ]
    )

    notes = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_transactions"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.ebqs_number} — {self.category}"

    def save(self, *args, **kwargs):
        if not self.tracking_id:
            self.tracking_id = (
                f"ECT-{uuid.uuid4().hex[:10].upper()}"
            )

        if not self.passkey:
            self.passkey = generate_passkey()

        super().save(*args, **kwargs)

class TransactionEvent(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name="events")
    event_type = models.CharField(max_length=30, choices=[("created","Created"),("stage_change","Stage change"),("pause","Clock pause/resume"),("completed","Completed")])
    stage = models.CharField(max_length=40)
    occurred_at = models.DateTimeField()
    reason = models.CharField(max_length=120, blank=True)
    remarks = models.TextField(blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="recorded_events")
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["occurred_at", "id"]
        indexes = [models.Index(fields=["transaction", "occurred_at"])]
