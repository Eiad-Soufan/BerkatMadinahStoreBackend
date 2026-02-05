from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator


# ======================
# Category
# ======================
class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)

    description = models.TextField(
        blank=True,
        help_text="Category description"
    )

    image_url = models.URLField(
        blank=True,
        help_text="External image URL for category"
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name



# ======================
# Product
# ======================
class Product(models.Model):
    category = models.ForeignKey(
        Category,
        related_name="products",
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)

    # 🔗 صورة خارجية
    image_url = models.URLField(
        blank=True,
        help_text="Used only if product has NO variants"
    )

    old_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    new_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    # 🧠 هل يوجد فاريانت؟
    @property
    def has_variants(self):
        return self.variants.exists()

    # 🧮 نسبة الخصم
    @property
    def discount_percentage(self):
        if self.old_price and self.old_price > self.new_price:
            return int(((self.old_price - self.new_price) / self.old_price) * 100)
        return 0

    def __str__(self):
        return self.name


# ======================
# Product Variant
# ======================
class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product,
        related_name="variants",
        on_delete=models.CASCADE
    )

    name = models.CharField(
        max_length=100,
        help_text="Example: 500g / Red / XL"
    )

    # 🔗 صورة خارجية لكل فاريانت
    image_url = models.URLField()

    old_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    new_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def discount_percentage(self):
        if self.old_price and self.old_price > self.new_price:
            return int(((self.old_price - self.new_price) / self.old_price) * 100)
        return 0

    def __str__(self):
        return f"{self.product.name} - {self.name}"
