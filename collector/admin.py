from django.contrib import admin
from .models import Transaction, TransactionEvent
class EventInline(admin.TabularInline): model=TransactionEvent; extra=0
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display=("ebqs_number","category","current_stage","status","final_label","received_at")
    list_filter=("status","category","final_label")
    search_fields=("ebqs_number","category")
    inlines=[EventInline]
admin.site.register(TransactionEvent)
