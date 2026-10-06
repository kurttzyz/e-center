import uuid
import secrets
import string

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone



class EmployeeProfile(models.Model):

    ROLE_CHOICES = [
        ("ojt", "OJT"),
        ("employee", "Employee"),
        ("supervisor", "Supervisor"),
        ("admin", "Administrator"),
    ]

    EMPLOYEE_TYPE_CHOICES = [
        ("ojt", "OJT"),
        ("regular", "Regular Employee"),
        ("contractual", "Contractual"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    position = models.CharField(
        max_length=100,
        blank=True,
    )

    office = models.CharField(
        max_length=100,
        default="E-Center",
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="employee",
    )

    employee_type = models.CharField(
        max_length=20,
        choices=EMPLOYEE_TYPE_CHOICES,
        default="ojt",
    )

    def __str__(self):
        return self.user.get_full_name() or self.user.username

def generate_passkey():
    characters = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(characters) for _ in range(8))


class ServiceCategory(models.Model):
    name = models.CharField(
        max_length=120,
        unique=True
    )

    description = models.TextField(
        blank=True
    )

    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Optional icon name"
    )

    display_order = models.PositiveIntegerField(
        default=0
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["display_order", "name"]
        verbose_name_plural = "Service categories"

    def __str__(self):
        return self.name


class Service(models.Model):
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.PROTECT,
        related_name="services"
    )

    name = models.CharField(
        max_length=200
    )

    code = models.SlugField(
        max_length=100,
        unique=True,
        db_index=True
    )

    description = models.TextField(
        blank=True
    )

    instructions = models.TextField(
        blank=True,
        help_text="Instructions shown to the client before proceeding"
    )

    threshold_minutes = models.PositiveIntegerField(
        default=30,
        help_text="Approved processing-time threshold in minutes",
        null=True,
    )

    is_online = models.BooleanField(
        default=True,
        help_text="Service can be assisted through the E-Center/My.SSS"
    )

    is_active = models.BooleanField(
        default=True
    )

    display_order = models.PositiveIntegerField(
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = [
            "category__display_order",
            "display_order",
            "name"
        ]

    def __str__(self):
        return self.name


class ServiceRequirement(models.Model):
    class RequirementType(models.TextChoices):
        DOCUMENT = "document", "Document"
        ACCOUNT = "account", "Account prerequisite"
        ELIGIBILITY = "eligibility", "Eligibility condition"
        INFORMATION = "information", "Information"
        OTHER = "other", "Other"

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="requirements",
        null=True,
        blank=True,
    )

    requirement_type = models.CharField(
        max_length=20,
        choices=RequirementType.choices,
        default=RequirementType.DOCUMENT
    )

    name = models.CharField(
        max_length=255
    )

    description = models.TextField(
        blank=True
    )

    is_required = models.BooleanField(
        default=True
    )

    display_order = models.PositiveIntegerField(
        default=0
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["display_order", "name"]

    def __str__(self):
        return f"{self.service.name} — {self.name}"


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

    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        related_name="transactions",
        null=True,
        blank=True,
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
        help_text="Approved category threshold in minutes",
        null=True,
        blank=True
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
        ],
        null=True,
  
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
            return f"{self.ebqs_number} — {self.service.name}"

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
