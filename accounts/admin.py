from django.contrib.admin import register, ModelAdmin
from django.contrib.auth.admin import UserAdmin
from .models import User

@register(User)
class CustomUserAdmin(UserAdmin):
    pass
