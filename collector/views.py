import csv
import base64
from io import BytesIO

import qrcode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction as db_transaction
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CompletionForm, EventForm, TransactionForm
from .models import Transaction, TransactionEvent

@login_required
def dashboard(request):
    query=request.GET.get("q","").strip()
    rows=Transaction.objects.all()
    if query: rows=rows.filter(Q(ebqs_number__icontains=query)|Q(category__icontains=query)|Q(current_stage__icontains=query))
    counts=Transaction.objects.aggregate(total=Count("id"),active=Count("id",filter=Q(status="active")),completed=Count("id",filter=Q(status="completed")),delayed=Count("id",filter=Q(final_label="delayed")))
    return render(request,"collector/dashboard.html",{"transactions":rows[:200],"counts":counts,"query":query})

@login_required
def create_transaction(request):
    form=TransactionForm(request.POST or None, initial={"received_at":timezone.localtime().strftime("%Y-%m-%dT%H:%M"),"requirements_status":"complete","priority_category":"regular"})
    if request.method=="POST" and form.is_valid():
        with db_transaction.atomic():
            item=form.save(False);item.created_by=request.user;item.save()
            TransactionEvent.objects.create(transaction=item,event_type="created",stage="received",occurred_at=item.received_at,remarks="Transaction registered",recorded_by=request.user)
        messages.success(request,"Transaction registered.");return redirect("qr_result",pk=item.pk) #it was transaction_detail vefore
    return render(request,"collector/form.html",{"form":form,"title":"Register transaction","submit_label":"Save research record"})

@login_required
def transaction_detail(request,pk):
    item=get_object_or_404(Transaction.objects.prefetch_related("events__recorded_by"),pk=pk)
    return render(request,"collector/detail.html",{"item":item})

@login_required
def add_event(request,pk):
    item=get_object_or_404(Transaction,pk=pk,status="active")
    form=EventForm(request.POST or None,initial={"occurred_at":timezone.localtime().strftime("%Y-%m-%dT%H:%M")})
    if request.method=="POST" and form.is_valid():
        event=form.save(False);event.transaction=item;event.recorded_by=request.user
        event.event_type="pause" if event.stage=="waiting_for_client" or (item.current_stage=="waiting_for_client" and event.stage=="processing") else "stage_change"
        with db_transaction.atomic():
            event.save();item.current_stage=event.stage
            if not item.accepted_at and event.stage=="requirements_checked": item.accepted_at=event.occurred_at
            item.save()
        messages.success(request,"Transaction event recorded.");return redirect("transaction_detail",pk=pk)
    return render(request,"collector/form.html",{"form":form,"title":f"Add event · {item.ebqs_number}","submit_label":"Record event"})

@login_required
def complete_transaction(request,pk):
    item=get_object_or_404(Transaction,pk=pk,status="active")
    form=CompletionForm(request.POST or None,initial={"completed_at":timezone.localtime().strftime("%Y-%m-%dT%H:%M")})
    if request.method=="POST" and form.is_valid():
        try:
            with db_transaction.atomic():
                item.complete(form.cleaned_data["completed_at"])
                TransactionEvent.objects.create(transaction=item,event_type="completed",stage="completed",occurred_at=item.completed_at,remarks=form.cleaned_data["remarks"],recorded_by=request.user)
            messages.success(request,f"Transaction labeled {item.get_final_label_display()}.");return redirect("transaction_detail",pk=pk)
        except ValidationError as exc: form.add_error(None,exc.message)
    return render(request,"collector/form.html",{"form":form,"title":f"Complete · {item.ebqs_number}","submit_label":"Complete and calculate label"})

@login_required
def export_csv(request):
    response=HttpResponse(content_type="text/csv");response["Content-Disposition"]='attachment; filename="ecenter-training-data.csv"'
    writer=csv.writer(response);writer.writerow(["research_id","ebqs_number","category","requirements_status","priority_category","received_at","accepted_at","threshold_minutes","status","completed_at","adjusted_duration_minutes","final_label","notes"])
    for x in Transaction.objects.order_by("received_at"): writer.writerow([x.pk,x.ebqs_number,x.category,x.requirements_status,x.priority_category,x.received_at,x.accepted_at,x.threshold_minutes,x.status,x.completed_at,x.adjusted_duration_minutes,x.final_label,x.notes])
    return response

# WEBSITE 

SERVICES = [
    {"group": "Services", "icon": "briefcase", "items": ["Disbursement Account", "My.SSS Card"]},
    {"group": "Benefits", "icon": "heart", "items": ["Maternity", "Sickness", "Disability", "Retirement", "Unemployment", "Funeral", "Death"]},
    {"group": "Loans", "icon": "wallet", "items": ["Pension Loan", "Emergency/Calamity Loan", "Penalty Loan Condonation"]},
]


def home(request):
    return render(request, "portal/home.html")


def services(request):
    return render(request, "portal/services.html", {"services": SERVICES})


def scan_qr(request):
    if request.method == "POST":
        if request.FILES.get("qr_image"):
            messages.success(request, "QR image received. Demo mode opened the sample transaction.")
            return redirect("transaction")
        messages.error(request, "Please choose a QR image first.")
    return render(request, "portal/scan.html")


def passkey(request):
    if request.method == "POST":
        code = request.POST.get("passkey", "").strip().upper()

        if not code:
            messages.error(
                request,
                "Please enter your transaction passkey."
            )
            return render(request, "portal/passkey.html")

        item = Transaction.objects.filter(
            passkey=code
        ).first()

        if not item:
            messages.error(
                request,
                "Invalid passkey. Please check your receipt and try again."
            )
            return render(request, "portal/passkey.html")

        return redirect(
            "transaction_status",
            tracking_id=item.tracking_id
        )

    return render(request, "portal/passkey.html")


def transaction_status(request, tracking_id):
    item = get_object_or_404(
        Transaction.objects.prefetch_related("events"),
        tracking_id=tracking_id
    )

    return render(
        request,
        "portal/transaction_status.html",
        {
            "transaction": item,
        }
    )

# def transaction(request):
#     if request.method == "POST":
#         tracking_id = f"ECT-{uuid4().hex[:10].upper()}"
#         request.session["tracking_id"] = tracking_id
#         request.session["transaction_type"] = request.POST.get("transaction_type", "E-Center Assistance")
#         return redirect("qr_result")
#     return render(request, "portal/transaction.html", {
#         "member": {"reference": "•••••••678", "name": "Sample Member"},
#         "submitted": ["Valid government-issued ID", "Member information form"],
#         "lacking": ["Validated deposit slip with visible name and account number"],
#     })


# def qr_result(request):
#     tracking_id = request.session.get("tracking_id", "ECT-DEMO2026")
#     passkey_value = uuid4().hex[:8].upper()
#     # The QR contains only a random tracking reference—never SS numbers, OTPs, or documents.
#     qr = qrcode.make(f"ECENTER-TRACKING:{tracking_id}")
#     stream = BytesIO()
#     qr.save(stream, format="PNG")
#     qr_data = base64.b64encode(stream.getvalue()).decode("ascii")
#     return render(request, "portal/qr_result.html", {
#         "tracking_id": tracking_id,
#         "passkey": passkey_value,
#         "qr_data": qr_data,
#     })
@login_required
def qr_result(request, pk):
    item = get_object_or_404(
        Transaction.objects.prefetch_related("events"),
        pk=pk
    )

    status_url = request.build_absolute_uri(
        f"/status/{item.tracking_id}/"
    )

    qr = qrcode.make(status_url)

    stream = BytesIO()
    qr.save(stream, format="PNG")

    qr_data = base64.b64encode(
        stream.getvalue()
    ).decode("ascii")

    return render(
        request,
        "portal/qr_result.html",
        {
            "transaction": item,
            "qr_data": qr_data,
        }
    )


# def generate_passkey():
#     characters = string.ascii_uppercase + string.digits
#     return "".join(secrets.choice(characters) for _ in range(8))

