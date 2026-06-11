from django.contrib import admin

from main.models import User


# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["username", "is_active", "telegram_id"]