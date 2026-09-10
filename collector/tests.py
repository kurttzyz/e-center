from datetime import timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from .models import Transaction, TransactionEvent

class LabelTests(TestCase):
    def setUp(self): self.user=get_user_model().objects.create_user("staff",password="test")
    def test_completion_labels_delayed(self):
        start=timezone.now()-timedelta(hours=30)
        item=Transaction.objects.create(ebqs_number="A-1",category="ACOP",requirements_status="complete",received_at=start,accepted_at=start,threshold_minutes=1440,created_by=self.user)
        item.complete(timezone.now())
        self.assertEqual(item.final_label,"delayed")
    def test_client_pause_is_subtracted(self):
        start=timezone.now()-timedelta(hours=30)
        item=Transaction.objects.create(ebqs_number="A-2",category="DAEM",requirements_status="complete",received_at=start,accepted_at=start,threshold_minutes=1440,created_by=self.user)
        TransactionEvent.objects.create(transaction=item,event_type="pause",stage="waiting_for_client",occurred_at=start+timedelta(hours=2),recorded_by=self.user)
        TransactionEvent.objects.create(transaction=item,event_type="pause",stage="processing",occurred_at=start+timedelta(hours=12),recorded_by=self.user)
        item.complete(timezone.now())
        self.assertEqual(item.final_label,"on_time")
