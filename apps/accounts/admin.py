from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.forms import (
    UserChangeForm,
    UserCreationForm,
    AdminPasswordChangeForm,
)
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group as DefaultGroup
from .models import User, Group

@admin.register(User)
class UserAdmin(UserAdmin, ModelAdmin):
    list_display    = ["email", "first_name", "last_name", "is_active"]
    search_fields   = ("email",)
    list_filter     = ("is_staff", "is_superuser")

    fieldsets = (
        ("User Credentials", {"fields": ("email", "first_name", "last_name", "dob", "location", "password")}),
        ("User Permissions", {"fields": ("is_active", "is_staff","is_admin", "is_superuser")}),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email","first_name", "last_name", "dob", "location", "password1", "is_staff", "is_active", "is_superuser"),
            },
        ),
    )
    ordering = ("email",)
    filter_horizontal = ()
    readonly_fields = ("last_login", "date_joined")
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm


@admin.register(Group)
class GroupAdmin(ModelAdmin):
    pass

admin.site.unregister(DefaultGroup)
