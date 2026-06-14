# Django Storefront

A white-label e-commerce storefront built with Django. Branding, currency,
payment gateways, social links, and contact details are all configured at
runtime from the Django admin — no per-client code changes.

## Features

- Products, categories, variants, reviews, cart, coupons, and orders (with PDF invoices)
- Admin-managed **Site settings**: store name, logo, favicon, currency (display symbol + ISO charge code), social links, contact-message inbox, and payment keys
- Payment gateways: **Stripe**, **Razorpay**, and **PayPal** — each independently toggleable, with a PayPal sandbox/live switch
- Contact form whose submissions are read in the admin

## Quick start

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/ and set up your store at **/admin/ → Core → Site settings**.

## Configuration

Local development runs on sensible defaults with no extra setup. For production,
copy `.env.example` to `.env` and set `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`,
and `SITE_URL`. Payment keys and all branding can be set either via environment
variables or per-store in the admin (the admin values take precedence).

## Deployment

`server_files/` contains example **gunicorn**, **supervisor**, and **nginx**
configs — replace the placeholder paths, user, and domain for your server.
