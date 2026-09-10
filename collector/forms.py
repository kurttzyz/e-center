from django import forms
from .models import Transaction, TransactionEvent

CATEGORIES = [(x,x) for x in ["ACOP","DAEM","Member data correction","Benefit inquiry","Contribution inquiry","Account assistance","Other"]]
STAGES = [("requirements_checked","Requirements checked"),("for_verification","For verification"),("processing","Processing / resume clock"),("waiting_for_client","Waiting for client / pause clock"),("approved","Approved")]
class DateTimeInput(forms.DateTimeInput): input_type = "datetime-local"
class TransactionForm(forms.ModelForm):
    threshold_hours = forms.IntegerField(min_value=1, label="Category threshold (hours)")
    category = forms.ChoiceField(choices=CATEGORIES)
    class Meta:
        model = Transaction
        fields = ["ebqs_number","category","requirements_status","priority_category","received_at","notes"]
        widgets = {"received_at":DateTimeInput(),"notes":forms.Textarea(attrs={"rows":3})}
    def save(self, commit=True):
        obj=super().save(False);obj.threshold_minutes=self.cleaned_data["threshold_hours"]*60
        if obj.requirements_status==Transaction.Requirements.COMPLETE: obj.accepted_at=obj.received_at
        if commit: obj.save()
        return obj
class EventForm(forms.ModelForm):
    stage = forms.ChoiceField(choices=STAGES)
    class Meta:
        model = TransactionEvent
        fields = ["stage","occurred_at","reason","remarks"]
        widgets = {"occurred_at":DateTimeInput(),"remarks":forms.Textarea(attrs={"rows":3})}
class CompletionForm(forms.Form):
    completed_at = forms.DateTimeField(widget=DateTimeInput())
    remarks = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows":3}))
