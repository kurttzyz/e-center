from django import forms

from .models import (
    Transaction,
    TransactionEvent,
    Service,
)


# ============================================================
# TRANSACTION STAGES
# ============================================================

STAGES = [
    ("requirements_checked", "Requirements Checked"),
    ("for_verification", "For Verification"),
    ("processing", "Processing"),
    ("waiting_for_client", "Waiting for Client"),
    ("approved", "Approved"),
    ("completed", "Completed"),
]


# ============================================================
# DATETIME INPUT
# ============================================================

class DateTimeInput(forms.DateTimeInput):
    input_type = "datetime-local"


# ============================================================
# TRANSACTION FORM
# ============================================================

class TransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction

        fields = [
            "ebqs_number",
            "service",
            "requirements_status",
            "priority_category",
            "received_at",
            "notes",
        ]

        labels = {
            "ebqs_number": "EBQS Number",
            "service": "E-Center Service",
            "requirements_status": "Requirements Status",
            "priority_category": "Priority Category",
            "received_at": "Date and Time Received",
            "notes": "Notes / Observations",
        }

        widgets = {
            "ebqs_number": forms.TextInput(
                attrs={
                    "placeholder": "Enter EBQS number",
                    "autocomplete": "off",
                }
            ),

            "received_at": DateTimeInput(
                attrs={
                    "step": "60",
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": (
                        "Enter non-personal transaction "
                        "observations if necessary."
                    ),
                }
            ),
        }

        help_texts = {
            "ebqs_number": (
                "Enter the queue or transaction reference number only."
            ),
            "service": (
                "Select the E-Center service being monitored."
            ),
            "received_at": (
                "Record when the transaction entered "
                "the monitoring process."
            ),
            "notes": (
                "Do not enter names, SSS numbers, contact details, "
                "or other personal information."
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Only display active E-Center services
        self.fields["service"].queryset = (
            Service.objects
            .filter(is_active=True)
            .order_by("display_order", "name")
        )

        self.fields["service"].empty_label = "Select E-Center service"

    def save(self, commit=True):

        obj = super().save(commit=False)

        # No manually entered threshold.
        # Duration/delay will be derived from transaction data.

        if obj.requirements_status == Transaction.Requirements.COMPLETE:
            obj.accepted_at = obj.received_at
        else:
            obj.accepted_at = None

        if commit:
            obj.save()

        return obj


# ============================================================
# EVENT FORM
# ============================================================

class EventForm(forms.ModelForm):

    stage = forms.ChoiceField(
        choices=STAGES,
        label="Transaction Stage",
    )

    class Meta:
        model = TransactionEvent

        fields = [
            "stage",
            "occurred_at",
            "reason",
            "remarks",
        ]

        labels = {
            "stage": "Transaction Stage",
            "occurred_at": "Date and Time",
            "reason": "Reason",
            "remarks": "Remarks / Observations",
        }

        widgets = {
            "occurred_at": DateTimeInput(
                attrs={
                    "step": "60",
                }
            ),

            "reason": forms.TextInput(
                attrs={
                    "placeholder": "Enter reason if applicable",
                    "autocomplete": "off",
                }
            ),

            "remarks": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": (
                        "Enter non-personal observations "
                        "about this event."
                    ),
                }
            ),
        }


# ============================================================
# COMPLETION FORM
# ============================================================

class CompletionForm(forms.Form):

    completed_at = forms.DateTimeField(
        label="Date and Time Completed",
        widget=DateTimeInput(
            attrs={
                "step": "60",
            }
        ),
    )

    remarks = forms.CharField(
        label="Completion Remarks",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": (
                    "Enter non-personal completion "
                    "observations if necessary."
                ),
            }
        ),
    )