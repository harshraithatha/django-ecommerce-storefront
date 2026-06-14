import os

from io import BytesIO

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles import finders
from django.template.loader import get_template
from django.http import HttpResponse
from django.conf import settings

from xhtml2pdf import pisa

from .models import Order


def pdf_link_callback(uri, rel):
    """Map MEDIA_URL/STATIC_URL references to absolute filesystem paths.

    xhtml2pdf cannot reliably fetch resources over HTTP, so resolving them to
    local files is what makes the logo, product thumbnails, and the bundled
    DejaVu font (declared via @font-face, needed for the ₹/€/etc glyphs) work.
    """
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri[len(settings.MEDIA_URL):])
    elif uri.startswith(settings.STATIC_URL):
        relative = uri[len(settings.STATIC_URL):]
        path = finders.find(relative) or os.path.join(settings.STATIC_ROOT or '', relative)
    else:
        return uri  # already absolute (http) or a local path; leave it alone

    return path if os.path.isfile(path) else uri


def render_to_pdf(template_src, context_dict={}):
    from apps.core.models import StoreSettings

    s = StoreSettings.load()
    template = get_template(template_src)
    context = {
        'currency_symbol': s.currency_symbol,
        'site_name': s.site_name,
        'site_url': settings.SITE_URL,
        'logo_url': s.logo.url if s.logo else '',
        **context_dict,
    }
    html = template.render(context)
    result = BytesIO()
    # UTF-8 so currency symbols like ₹ € ₩ ₽ encode correctly (Latin-1 cannot).
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, encoding='UTF-8',
                            link_callback=pdf_link_callback)

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
            content = "attachment; filename=%s.pdf" % (order.order_number or order_id)
            response['Content-Disposition'] = content

            return response
    
    return HttpResponse("Not found")