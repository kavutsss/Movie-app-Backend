from django.contrib import admin

from .models import Club, ClubMember


class ClubMemberInline(admin.TabularInline):
    model = ClubMember
    extra = 0
    readonly_fields = ['user', 'joined_at']


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'genre', 'status', 'created_by', 'member_count', 'created_at']
    list_filter = ['status', 'genre']
    search_fields = ['name', 'description', 'created_by__email']
    list_editable = ['status']
    readonly_fields = ['created_at', 'created_by']
    ordering = ['name']
    inlines = [ClubMemberInline]

    def member_count(self, obj):
        return obj.memberships.count()
    member_count.short_description = 'Members'
