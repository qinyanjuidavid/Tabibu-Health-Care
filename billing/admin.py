from django.contrib import admin
from billing.models import MpesaPayment, MpesaCallBacks, MpesaCalls


@admin.register(MpesaPayment)
class MpesaPaymentAdmin(admin.ModelAdmin):
    list_display = ("reference", "first_name", "middle_name",
                    "last_name", "phone_number", "amount", "type",
                    "organization_balance")
    list_filter = ("type",)


admin.site.register(MpesaCallBacks)
admin.site.register(MpesaCalls)
