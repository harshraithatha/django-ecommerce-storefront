from django.db import migrations
from django.utils import timezone


def backfill_order_numbers(apps, schema_editor):
    """Assign YYMMDD + daily-sequence numbers to pre-existing orders."""
    Order = apps.get_model('order', 'Order')
    counters = {}

    for order in Order.objects.order_by('created_at', 'pk'):
        if order.order_number:
            continue

        date_part = timezone.localtime(order.created_at).strftime('%y%m%d')
        counters[date_part] = counters.get(date_part, 0) + 1
        order.order_number = '%s%02d' % (date_part, counters[date_part])
        order.save(update_fields=['order_number'])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0011_order_order_number'),
    ]

    operations = [
        migrations.RunPython(backfill_order_numbers, noop),
    ]
