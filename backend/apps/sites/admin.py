from django.contrib import admin
from .models import (
    Site, Page, Template, Component, MediaLibrary, Form, FormSubmission,
)


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ("name", "org", "status", "custom_domain", "created_at")
    list_filter = ("status",)
    search_fields = ("name", "org__name")


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("title", "site", "path", "status", "sort_order")
    list_filter = ("status",)
    search_fields = ("title", "site__name")


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "is_premium", "is_active", "sort_order")
    list_filter = ("category", "is_premium", "is_active")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "is_active")
    list_filter = ("category", "is_active")


@admin.register(MediaLibrary)
class MediaLibraryAdmin(admin.ModelAdmin):
    list_display = ("filename", "org", "file_type", "file_size", "created_at")
    list_filter = ("file_type",)


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ("name", "site", "is_active", "created_at")


@admin.register(FormSubmission)
class FormSubmissionAdmin(admin.ModelAdmin):
    list_display = ("form", "ip_address", "created_at")
    readonly_fields = ("data",)
