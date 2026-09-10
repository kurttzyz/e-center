from django.urls import path
from . import views
urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("transactions/new/", views.create_transaction, name="transaction_create"),
    path("transactions/<uuid:pk>/", views.transaction_detail, name="transaction_detail"),
    path("transactions/<uuid:pk>/event/", views.add_event, name="event_add"),
    path("transactions/<uuid:pk>/complete/", views.complete_transaction, name="transaction_complete"),
    path("export/training-data.csv", views.export_csv, name="export_csv"),

    path("homepage/", views.home, name="home"),
    path("services/", views.services, name="services"),
    path("scan/", views.scan_qr, name="scan"),
    path("passkey/", views.passkey, name="passkey"),
    path("transaction/", views.transaction, name="transaction"),
    path("qr-result/", views.qr_result, name="qr_result"),
]
