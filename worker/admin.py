from django.contrib import admin
from .models import TaskerProfile


@admin.register(TaskerProfile)
class TaskerProfileAdmin(admin.ModelAdmin):
    # Shows all these columns in the Django Default Admin
    list_display = ('totooid', 'user', 'phone_number', 'is_approved')

    # ADD THIS LINE: This makes the 'is_approved' column a clickable checkbox in the list view!
    list_editable = ('is_approved',)

    list_filter = ('is_approved',)
    search_fields = ('totooid', 'user__username', 'user__email')
    readonly_fields = ('totooid',)  # Prevents admin from manually changing the auto-ID