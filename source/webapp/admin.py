from django.contrib import admin
from .models import Issue, Status, Type, Project


class IssueAdmin(admin.ModelAdmin):
    filter_horizontal = ('type',)
    list_filter = ('status',)
    list_display = ('pk', 'summary',)
    list_display_links = ('pk', 'summary')
    search_fields = ('type',)


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('pk', 'is_deleted', 'name',)
    list_display_links = ('pk', 'name')
    filter_horizontal = ('team',)
    search_fields = ('name',)


admin.site.register(Issue, IssueAdmin)
admin.site.register(Status)
admin.site.register(Type)
admin.site.register(Project, ProjectAdmin)


