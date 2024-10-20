from django.contrib import admin
from unfold.admin import ModelAdmin
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.token_blacklist.admin import OutstandingTokenAdmin, BlacklistedTokenAdmin, AuthUser


admin.site.unregister(OutstandingToken)
@admin.register(OutstandingToken)
class OutstandingTokenAdmin(ModelAdmin):
    list_display = (
        "jti",
        "user",
        "created_at",
        "expires_at",
    )
    search_fields = (
        "jti",
        "user__id",
        "user__email",
    )
    ordering = ("user",)
    readonly_fields = ["token", "jti"]
   
    def has_add_permission(self, *args, **kwargs) -> bool:
        return True

    def has_delete_permission(self, *args, **kwargs) -> bool:
        return True


admin.site.unregister(BlacklistedToken)
@admin.register(BlacklistedToken)
class BlacklistedTokenAdmin(ModelAdmin, BlacklistedTokenAdmin):
    list_display = (
        "token_jti",
        "token_user",
        "token_created_at",
        "token_expires_at",
        "blacklisted_at",
    )
    search_fields = (
        "token__user__id",
        "token__jti",
    )
    ordering = ("token__user",)
    readonly_fields = []

    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, *args, **kwargs) -> bool:
        return True