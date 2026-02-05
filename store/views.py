from rest_framework import viewsets
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    lookup_field = "slug"


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSerializer
    lookup_field = "slug"

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True).select_related("category").prefetch_related("variants")

        category_slug = self.request.query_params.get("category")
        if category_slug and category_slug != "all":
            qs = qs.filter(category__slug=category_slug)

        return qs
