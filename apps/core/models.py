from django.db import models
from django.conf import settings


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=150)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Contact message'
        verbose_name_plural = 'Contact messages'

    def __str__(self):
        return '%s — %s' % (self.subject, self.name)


class SocialLink(models.Model):
    title = models.CharField(max_length=50)
    url = models.URLField()
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('order', 'title')
        verbose_name = 'Social link'
        verbose_name_plural = 'Social links'

    def __str__(self):
        return self.title


class StoreSettings(models.Model):
    CURRENCY_CHOICES = [
        ('$', 'Dollar ($)'),
        ('₹', 'Indian Rupee (₹)'),
        ('€', 'Euro (€)'),
        ('£', 'British Pound (£)'),
        ('¥', 'Yen / Yuan (¥)'),
        ('₩', 'Korean Won (₩)'),
        ('₽', 'Russian Ruble (₽)'),
        ('A$', 'Australian Dollar (A$)'),
        ('C$', 'Canadian Dollar (C$)'),
        ('R$', 'Brazilian Real (R$)'),
    ]

    site_name = models.CharField(max_length=100, default='My Store')
    logo = models.ImageField(
        upload_to='site/', blank=True, null=True,
        help_text='Shown top-left in the navbar. A transparent PNG with light artwork works best on the dark navbar. Leave blank to show the site name as text.'
    )
    favicon = models.ImageField(
        upload_to='site/', blank=True, null=True,
        help_text='Browser-tab icon. A small square PNG (e.g. 32×32 or 48×48) is recommended; .ico also works.'
    )
    currency_symbol = models.CharField(max_length=8, choices=CURRENCY_CHOICES, default='$')
    currency_code = models.CharField(
        max_length=3, default='USD',
        help_text='ISO code used to charge customers, e.g. USD, INR, EUR, GBP, JPY. (Razorpay supports INR primarily.)'
    )
    from_email = models.EmailField(
        default='noreply@example.com',
        help_text='Sender address used for order emails.'
    )
    notification_email = models.EmailField(
        default='orders@example.com',
        help_text='Store address that receives a copy of each order.'
    )

    # Payment gateway keys — leave blank to fall back to the values in settings.py
    stripe_publishable_key = models.CharField('Stripe publishable key', max_length=255, blank=True, default='')
    stripe_secret_key = models.CharField('Stripe secret key', max_length=255, blank=True, default='')
    razorpay_publishable_key = models.CharField('Razorpay key id', max_length=255, blank=True, default='')
    razorpay_secret_key = models.CharField('Razorpay key secret', max_length=255, blank=True, default='')
    paypal_publishable_key = models.CharField('PayPal client id', max_length=255, blank=True, default='')
    paypal_secret_key = models.CharField('PayPal secret', max_length=255, blank=True, default='')

    # Enable/disable each gateway on the checkout page
    stripe_enabled = models.BooleanField('Stripe enabled', default=False)
    razorpay_enabled = models.BooleanField('Razorpay enabled', default=True)
    paypal_enabled = models.BooleanField('PayPal enabled', default=False)
    paypal_sandbox = models.BooleanField(
        'PayPal sandbox mode', default=True,
        help_text='On = PayPal sandbox (testing). Turn off for live payments; must match the type of PayPal keys you entered.'
    )

    class Meta:
        verbose_name = 'Site settings'
        verbose_name_plural = 'Site settings'

    # Singleton: there is only ever one settings row.
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return 'Site settings'

    @classmethod
    def load(cls):
        # The single settings row, or an unsaved instance carrying the defaults.
        return cls.objects.first() or cls()

    @classmethod
    def get_symbol(cls):
        return cls.load().currency_symbol

    # Payment keys resolve to the admin value, falling back to settings.py when blank.
    @property
    def stripe_publishable(self):
        return self.stripe_publishable_key or getattr(settings, 'STRIPE_API_KEY_PUBLISHABLE', '')

    @property
    def stripe_secret(self):
        return self.stripe_secret_key or getattr(settings, 'STRIPE_API_KEY_HIDDEN', '')

    @property
    def razorpay_publishable(self):
        return self.razorpay_publishable_key or getattr(settings, 'RAZORPAY_API_KEY_PUBLISHABLE', '')

    @property
    def razorpay_secret(self):
        return self.razorpay_secret_key or getattr(settings, 'RAZORPAY_API_KEY_HIDDEN', '')

    @property
    def paypal_publishable(self):
        return self.paypal_publishable_key or getattr(settings, 'PAYPAL_API_KEY_PUBLISHABLE', '')

    @property
    def paypal_secret(self):
        return self.paypal_secret_key or getattr(settings, 'PAYPAL_API_KEY_HIDDEN', '')
