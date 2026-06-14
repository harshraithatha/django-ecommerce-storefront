from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from apps.store.models import Product

class Order(models.Model):
    ORDERED = 'ordered'
    SHIPPED = 'shipped'
    ARRIVED = 'arrived'

    STATUS_CHOICES = (
        (ORDERED, 'Ordered'),
        (SHIPPED, 'Shipped'),
        (ARRIVED, 'Arrived')
    )

    user = models.ForeignKey(User, related_name='orders', on_delete=models.SET_NULL, blank=True, null=True)

    # Human-friendly receipt number: YYMMDD + a sequence that resets each day
    # (e.g. 26061404 = 4th order on 2026-06-14). Assigned once, on creation.
    order_number = models.CharField(max_length=20, unique=True, blank=True, null=True, editable=False)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=100)
    place = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

    paid = models.BooleanField(default=False)
    paid_amount = models.FloatField(blank=True, null=True)
    used_coupon = models.CharField(max_length=50, blank=True, null=True)

    payment_intent = models.CharField(max_length=255)

    shipped_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ORDERED)

    def __str__(self):
        return self.order_number or ('Order %s' % self.pk)

    def save(self, *args, **kwargs):
        # created_at (auto_now_add) and pk only exist after the first save, and
        # the daily sequence depends on created_at, so number it in a second pass.
        assigning_number = self._state.adding and not self.order_number
        super().save(*args, **kwargs)

        if assigning_number and not self.order_number:
            self.order_number = self.build_order_number()
            super().save(update_fields=['order_number'])

    def build_order_number(self):
        local_dt = timezone.localtime(self.created_at)
        date_part = local_dt.strftime('%y%m%d')

        # Sequence = orders already placed that day + 1, bumped past any clash
        # (handles the rare concurrent-checkout race against the unique index).
        seq = Order.objects.filter(created_at__date=local_dt.date()).exclude(pk=self.pk).count() + 1
        while True:
            candidate = '%s%02d' % (date_part, seq)
            if not Order.objects.filter(order_number=candidate).exists():
                return candidate
            seq += 1

    def get_total_quantity(self):
        return sum(int(item.quantity) for item in self.items.all())

    def get_subtotal(self):
        return sum(item.get_cost() for item in self.items.all())

    def get_discount(self):
        # The gap between what the items cost and what was actually paid.
        if self.used_coupon and self.paid_amount is not None:
            return self.get_subtotal() - self.paid_amount
        return 0

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='items', on_delete=models.SET_NULL, blank=True, null=True)
    # Snapshot of the product name at checkout, so the receipt stays valid even
    # if the product is later renamed or deleted (product FK is SET_NULL).
    product_title = models.CharField(max_length=255, blank=True, default='')
    price = models.FloatField()
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return '%s' % self.id

    def get_title(self):
        if self.product_title:
            return self.product_title
        if self.product:
            return self.product.title
        return '(item no longer available)'

    def get_cost(self):
        # price is the unit price captured at checkout time.
        return self.price * self.quantity