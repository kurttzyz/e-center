import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ebqs_number = models.CharField(max_length=40, db_index=True)
    category = models.CharField(max_length=120, db_index=True)
    requirements_status = models.CharField(max_length=20, choices=Requirements.choices)
    priority_category = models.CharField(max_length=30, choices=Priority.choices, default=Priority.REGULAR)
    received_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)
    threshold_minutes = models.PositiveIntegerField(help_text="Approved category threshold in minutes")
    current_stage = models.CharField(max_length=40, default="received")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE, db_index=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    adjusted_duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    final_label = models.CharField(max_length=20, blank=True, choices=[("on_time","On time"),("delayed","Delayed")])
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="created_transactions")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-updated_at"]
    def __str__(self): return f"{self.ebqs_number} — {self.category}"
    def paused_minutes(self, until=None):
        until = until or timezone.now(); total = 0; started = None
        for event in self.events.filter(event_type="pause").order_by("occurred_at"):
            if event.stage == "waiting_for_client" and started is None: started = event.occurred_at
            elif event.stage == "processing" and started is not None:
                total += max(0, int((event.occurred_at-started).total_seconds()//60)); started = None
        if started: total += max(0, int((until-started).total_seconds()//60))
        return total
    def complete(self, completed_at):
        if not self.accepted_at: raise ValidationError("Requirements must be accepted before completion.")
        elapsed = max(0, int((completed_at-self.accepted_at).total_seconds()//60))
        self.adjusted_duration_minutes = max(0, elapsed-self.paused_minutes(completed_at))
        self.completed_at = completed_at
        self.final_label = "delayed" if self.adjusted_duration_minutes > self.threshold_minutes else "on_time"
        self.current_stage = "completed"; self.status = self.Status.COMPLETED
        self.save()

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
