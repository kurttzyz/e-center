from django.contrib import admin
from .models import Transaction, TransactionEvent
class EventInline(admin.TabularInline): model=TransactionEvent; extra=0
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display=("ebqs_number","service","current_stage","status","final_label","received_at")
    list_filter=("status","service","final_label")
    search_fields=("ebqs_number","service")
    inlines=[EventInline]
admin.site.register(TransactionEvent)


from django.contrib import admin

from .models import (
    ServiceCategory,
    Service,
    ServiceRequirement,
    Transaction,
    TransactionEvent,
)


class ServiceRequirementInline(admin.TabularInline):
    model = ServiceRequirement
    extra = 1

    fields = (
        "requirement_type",
        "name",
        "description",
        "is_required",
        "display_order",
        "is_active",
    )


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "display_order",
        "is_active",
    )

    list_editable = (
        "display_order",
        "is_active",
    )

    search_fields = ("name",)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "threshold_minutes",
        "is_online",
        "is_active",
        "display_order",
    )

    list_filter = (
        "category",
        "is_online",
        "is_active",
    )

    search_fields = (
        "name",
        "code",
        "description",
    )

    prepopulated_fields = {
        "code": ("name",)
    }

    inlines = [
        ServiceRequirementInline
    ]


@admin.register(ServiceRequirement)
class ServiceRequirementAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "service",
        "requirement_type",
        "is_required",
        "is_active",
    )

    list_filter = (
        "requirement_type",
        "is_required",
        "is_active",
    )

    search_fields = (
        "name",
        "service__name",
    )