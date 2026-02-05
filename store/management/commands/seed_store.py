from decimal import Decimal
from urllib.parse import quote

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from store.models import Category, Product, ProductVariant


def unique_slug_for_model(model_cls, base_text: str, slug_field: str = "slug") -> str:
    base_slug = slugify(base_text) or "item"
    slug = base_slug
    i = 2
    while model_cls.objects.filter(**{slug_field: slug}).exists():
        slug = f"{base_slug}-{i}"
        i += 1
    return slug


def safe_img(text: str, w: int = 900, h: int = 900) -> str:
    """
    Guaranteed working image URL (placeholder).
    Always returns an image even if repeated.
    """
    label = quote((text or "image")[:40])
    return f"https://placehold.co/{w}x{h}/111827/FFFFFF.png?text={label}"


class Command(BaseCommand):
    help = "Seed DB with 5 categories, each has 10 products (8 with variants)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing Categories/Products/Variants before seeding.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        reset = options.get("reset", False)

        if reset:
            ProductVariant.objects.all().delete()
            Product.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(self.style.WARNING("Reset done: deleted Categories/Products/Variants."))

        # -----------------------
        # Seed configuration
        # -----------------------
        categories = [
            "Beverages",
            "Snacks",
            "Grocery",
            "Personal Care",
            "Home & Kitchen",
        ]

        # 10 products per category:
        # first 8 => WITH variants, last 2 => NO variants
        product_names = [
            "Premium Item A",
            "Premium Item B",
            "Premium Item C",
            "Premium Item D",
            "Premium Item E",
            "Premium Item F",
            "Premium Item G",
            "Premium Item H",
            "Standard Item I",
            "Standard Item J",
        ]

        # Variants template
        variant_names = ["Small", "Medium", "Large"]

        created_categories = 0
        created_products = 0
        created_variants = 0

        for c_idx, cat_name in enumerate(categories, start=1):
            cat, cat_created = Category.objects.get_or_create(
                name=cat_name,
                defaults={
                    "slug": unique_slug_for_model(Category, cat_name),
                    "description": f"Auto-seeded category: {cat_name}",
                    "image_url": safe_img(f"Category {cat_name}", 1200, 600),
                    "is_active": True,
                },
            )
            if cat_created:
                created_categories += 1

            for p_idx, base_pname in enumerate(product_names, start=1):
                # Make product name unique per category
                pname = f"{base_pname} ({cat_name} #{p_idx})"

                # Simple pricing
                new_price = Decimal("5.00") + Decimal(str(c_idx)) + (Decimal(str(p_idx)) / Decimal("2"))
                old_price = (new_price + Decimal("2.50")) if (p_idx % 2 == 0) else None

                product, prod_created = Product.objects.get_or_create(
                    category=cat,
                    name=pname,
                    defaults={
                        "slug": unique_slug_for_model(Product, pname),
                        "description": f"Auto-seeded product in {cat_name}.",
                        "image_url": "",  # will be set only if NO variants
                        "old_price": old_price,
                        "new_price": new_price,
                        "is_active": True,
                    },
                )

                if prod_created:
                    created_products += 1

                has_variants = p_idx <= 8  # first 8 products have variants

                if has_variants:
                    # Ensure product image is blank when variants exist
                    if product.image_url:
                        product.image_url = ""
                        product.save(update_fields=["image_url"])

                    for v_idx, vname in enumerate(variant_names, start=1):
                        v_new = new_price + Decimal(str(v_idx))  # variant price differs
                        v_old = (v_new + Decimal("1.00")) if (v_idx == 2) else None

                        variant, v_created = ProductVariant.objects.get_or_create(
                            product=product,
                            name=vname,
                            defaults={
                                "image_url": safe_img(f"{pname} {vname}", 900, 900),
                                "old_price": v_old,
                                "new_price": v_new,
                                "stock": 20 + (v_idx * 5),
                                "is_active": True,
                            },
                        )
                        if v_created:
                            created_variants += 1
                else:
                    # No variants => put image on Product
                    if not product.image_url:
                        product.image_url = safe_img(pname, 900, 900)
                        product.save(update_fields=["image_url"])

        self.stdout.write(self.style.SUCCESS("Seeding completed ✅"))
        self.stdout.write(f"Categories created: {created_categories}")
        self.stdout.write(f"Products created:   {created_products}")
        self.stdout.write(f"Variants created:   {created_variants}")
        self.stdout.write(self.style.NOTICE("Run: python manage.py seed_store  (or reset: python manage.py seed_store --reset)"))
