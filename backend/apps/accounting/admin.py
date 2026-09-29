from django.contrib import admin

from apps.accounting.models import Account, JournalEntry, JournalLine


class JournalLineInline(admin.TabularInline):
    model = JournalLine
    extra = 0
    autocomplete_fields = ("account",)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "account_type",
        "is_active",
        "is_system",
        "parent",
    )
    list_filter = ("account_type", "is_active", "is_system")
    search_fields = ("code", "name")
    ordering = ("code",)


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "entry_date",
        "source_type",
        "source_id",
        "source_key",
        "memo",
        "posted_at",
    )
    list_filter = ("source_type", "entry_date")
    search_fields = ("memo", "source_id", "source_key")
    inlines = [JournalLineInline]
    readonly_fields = ("posted_at", "created_at")
