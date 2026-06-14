from django.contrib import admin

from .models import ContactMessage, SocialLink, StoreSettings


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'email', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    list_editable = ('is_read',)
    search_fields = ('name', 'email', 'subject', 'message')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')
    actions = ('mark_as_read', 'mark_as_unread')

    # Messages should only arrive via the contact form, not be typed in here.
    def has_add_permission(self, request):
        return False

    @admin.action(description='Mark selected messages as read')
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

    @admin.action(description='Mark selected messages as unread')
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'order', 'is_active')
    list_editable = ('url', 'order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'url')


@admin.register(StoreSettings)
class StoreSettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'site_name', 'currency_symbol')
    fieldsets = (
        ('Branding', {'fields': ('site_name', 'logo', 'favicon')}),
        ('Store', {'fields': ('currency_symbol', 'currency_code')}),
        ('Email', {'fields': ('from_email', 'notification_email')}),
        ('Stripe', {'fields': ('stripe_enabled', 'stripe_publishable_key', 'stripe_secret_key')}),
        ('Razorpay', {'fields': ('razorpay_enabled', 'razorpay_publishable_key', 'razorpay_secret_key')}),
        ('PayPal', {'fields': ('paypal_enabled', 'paypal_sandbox', 'paypal_publishable_key', 'paypal_secret_key')}),
    )

    # Singleton: allow creating the row only if none exists, and never delete it.
    def has_add_permission(self, request):
        return not StoreSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
