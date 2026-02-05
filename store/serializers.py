from rest_framework import serializers
from .models import Category, Product, ProductVariant


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "image_url",
        ]



class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = [
            "id",
            "name",
            "image_url",
            "new_price",
            "stock",
        ]


class ProductSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "image_url",
            "old_price",      # ✅ ADD THIS
            "new_price",
            "category",
            "variants",
        ]
