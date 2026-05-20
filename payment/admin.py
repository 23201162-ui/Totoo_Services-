from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user_transaction_id', 'tasker_transaction_id', 'service_user_role_id', 'tasker_toto_id', 'money_amount_sent', 'money_amount_given', 'payment_date')
    search_fields = ('user_transaction_id', 'tasker_transaction_id', 'service_user_role_id', 'tasker_toto_id')
    readonly_fields = ('money_amount_given', 'platform_retained', 'user_transaction_id', 'tasker_transaction_id', 'payment_date')
    ordering = ('-payment_date',)