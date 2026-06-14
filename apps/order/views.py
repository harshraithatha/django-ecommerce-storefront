from io import BytesIO

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template
from django.http import HttpResponse
from django.conf import settings

from xhtml2pdf import pisa

from .models import Order

def render_to_pdf(template_src, context_dict={}):
    from apps.core.models import StoreSettings

    s = StoreSettings.load()
    template = get_template(template_src)
    context = {'currency_symbol': s.currency_symbol, 'site_name': s.site_name, 'site_url': settings.SITE_URL, **context_dict}
    html = template.render(context)
    result = BytesIO()
    # UTF-8 so currency symbols like ₹ € ₩ ₽ encode correctly (Latin-1 cannot).
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, encoding='UTF-8')

    if not pdf.err:
        return result.getvalue()

    return None

@login_required
def admin_order_pdf(request, order_id):
    if request.user.is_superuser:
        order = get_object_or_404(Order, pk=order_id)
        pdf = render_to_pdf('order_pdf.html', {'order': order})

        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            content = "attachment; filename=%s.pdf" % order_id
            response['Content-Disposition'] = content

            return response
    
    return HttpResponse("Not found")