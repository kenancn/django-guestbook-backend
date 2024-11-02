from django.contrib import admin
from .models import GuestbookUser, GuestbookEntry


@admin.register(GuestbookUser)
class GuestbookUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    ordering = ('-created_at',)


@admin.register(GuestbookEntry)
class GuestbookEntryAdmin(admin.ModelAdmin):
    list_display = ('subject', 'user', 'created_at')
    list_filter = ('user',)
    search_fields = ('subject', 'message', 'user__name')
    ordering = ('-created_at',)
