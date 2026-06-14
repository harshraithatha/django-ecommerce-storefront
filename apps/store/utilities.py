from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from apps.order.views import render_to_pdf
from django.http import HttpResponse

def decrement_product_quantity(order):
    for item in order.items.all():
        product = item.product
        product.num_available = product.num_available - item.quantity
        product.save()

def send_order_confirmation(order):
    from apps.core.models import StoreSettings

    s = StoreSettings.load()
    subject = '%s - Order confirmation' % s.site_name
    from_email = s.from_email
    to = [s.notification_email, order.email]
    text_content = 'Your order is successful!'
    html_content = render_to_string('order_confirmation.html', {'order': order, 'currency_symbol': s.currency_symbol, 'site_name': s.site_name})

    pdf = render_to_pdf('order_pdf.html', {'order': order})

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")

    if pdf:
        name = 'order_%s.pdf' % order.id
        msg.attach(name, pdf, 'application/pdf')
    
    msg.send()