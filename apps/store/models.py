import os

from io import BytesIO
from django.core.files import File
from django.db import models
from PIL import Image
from django.contrib.auth.models import User

THUMBNAIL_SIZE = (600, 600)


def make_thumbnail(fieldfile, size=THUMBNAIL_SIZE):
    """Build a high-quality JPEG thumbnail from an image field file.

    Returns a ``File`` whose name is just the cleaned base name (e.g.
    ``IMG_9174_thumb.jpg``); the destination directory is decided by the
    field's ``upload_to`` callable, so the name passed here must not include
    a path.
    """
    fieldfile.open()
    img = Image.open(fieldfile)
    img = img.convert('RGB')
    img.thumbnail(size, Image.LANCZOS)

    thumb_io = BytesIO()
    img.save(thumb_io, 'JPEG', quality=90, optimize=True)

    base = os.path.splitext(os.path.basename(fieldfile.name))[0]

    return File(thumb_io, name='%s_thumb.jpg' % base)


def product_image_path(instance, filename):
    return 'products/%s/original/%s' % (instance.slug, filename)


def product_thumbnail_path(instance, filename):
    return 'products/%s/thumbs/%s' % (instance.slug, filename)


def gallery_image_path(instance, filename):
    return 'products/%s/gallery/original/%s' % (instance.product.slug, filename)


def gallery_thumbnail_path(instance, filename):
    return 'products/%s/gallery/thumbs/%s' % (instance.product.slug, filename)


class Category(models.Model):
    parent = models.ForeignKey('self', related_name='children', on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    ordering = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ('ordering',)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return '/%s/' % (self.slug)

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    parent = models.ForeignKey('self', related_name='variants', on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.FloatField()
    is_featured = models.BooleanField(default=False)
    num_available = models.IntegerField(default=1)
    num_visits = models.IntegerField(default=0)
    last_visit = models.DateTimeField(blank=True, null=True)

    image = models.ImageField(upload_to=product_image_path, blank=True, null=True)
    thumbnail = models.ImageField(upload_to=product_thumbnail_path, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-date_added',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_image = self.image.name

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.image and (self.image.name != self._original_image or not self.thumbnail):
            self.thumbnail = make_thumbnail(self.image)

        super().save(*args, **kwargs)
        self._original_image = self.image.name

    def get_absolute_url(self):
        return '/%s/%s/' % (self.category.slug, self.slug)

    def get_thumbnail(self):
        if self.thumbnail:
            return self.thumbnail.url
        elif self.image:
            self.thumbnail = make_thumbnail(self.image)
            self.save()

            return self.thumbnail.url
        else:
            return ''

    def get_rating(self):
        total = sum(int(review['stars']) for review in self.reviews.values())

        if self.reviews.count() > 0:
            return total / self.reviews.count()
        else:
            return 0

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)

    image = models.ImageField(upload_to=gallery_image_path, blank=True, null=True)
    thumbnail = models.ImageField(upload_to=gallery_thumbnail_path, blank=True, null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_image = self.image.name

    def save(self, *args, **kwargs):
        if self.image and (self.image.name != self._original_image or not self.thumbnail):
            self.thumbnail = make_thumbnail(self.image)

        super().save(*args, **kwargs)
        self._original_image = self.image.name

class ProductReview(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)

    content = models.TextField(blank=True, null=True)
    stars = models.IntegerField()

    date_added = models.DateTimeField(auto_now_add=True)