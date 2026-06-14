from django.db import migrations


def backfill_product_title(apps, schema_editor):
    """Snapshot the current product title onto existing order items.

    Items whose product was already deleted (product is null) keep an empty
    title and fall back to a placeholder when displayed.
    """
    OrderItem = apps.get_model('order', 'OrderItem')

    for item in OrderItem.objects.filter(product_title='').select_related('product'):
        if item.product:
            item.product_title = item.product.title
            item.save(update_fields=['product_title'])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0013_orderitem_product_title'),
    ]

    operations = [
        migrations.RunPython(backfill_product_title, noop),
    ]
