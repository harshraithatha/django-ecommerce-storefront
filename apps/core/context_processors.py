from .models import SocialLink, StoreSettings


def social_links(request):
    return {'social_links': SocialLink.objects.filter(is_active=True)}


def store_settings(request):
    s = StoreSettings.load()
    return {
        'currency_symbol': s.currency_symbol,
        'currency_code': s.currency_code,
        'site_name': s.site_name,
        'site_logo': s.logo.url if s.logo else None,
        'site_favicon': s.favicon.url if s.favicon else None,
    }
