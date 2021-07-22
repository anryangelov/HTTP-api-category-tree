from django.contrib import admin

from category_tree_app.models import Category


@admin.register(Category)
class AuthorAdmin(admin.ModelAdmin):
    pass
