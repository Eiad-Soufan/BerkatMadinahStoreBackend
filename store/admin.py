from django.contrib import admin
from .models import Category, Product, ProductVariant


# =========================
# Variant Inline (داخل المنتج)
# =========================
class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = (
        "name",
        "image_url",
        "old_price",
        "new_price",
        "stock",
        "is_active",
    )
    readonly_fields = ()
    show_change_link = True


# =========================
# Product Admin
# =========================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "new_price",
        "discount_percentage",
        "has_variants",
        "is_active",
        "created_at",
    )

    list_filter = (
        "category",
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "description",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }

    inlines = [ProductVariantInline]

    fieldsets = (
        ("Basic Information", {
            "fields": (
                "category",
                "name",
                "slug",
                "description",
                "is_active",
            )
        }),
        ("Pricing (used only if NO variants)", {
            "fields": (
                "old_price",
                "new_price",
            )
        }),
        ("Product Image (External URL)", {
            "fields": (
                "image_url",
            )
        }),
    )


# =========================
# Category Admin
# =========================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_active",
    )

    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

    fieldsets = (
        ("Basic Information", {
            "fields": (
                "name",
                "slug",
                "is_active",
            )
        }),
        ("Category Details", {
            "fields": (
                "description",
                "image_url",
            )
        }),
    )


# =========================
# Variant Admin (Standalone)
# =========================
@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "name",
        "new_price",
        "stock",
        "is_active",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "product__name",
        "name",
    )
