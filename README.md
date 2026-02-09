# Vantor — Premium Skincare E-commerce Platform

A production-ready Django e-commerce platform designed for a modern luxury skincare brand.  
Built with scalability, performance, and clean UX in mind.

---

## Overview

Vantor is a modular Django e-commerce system that focuses on:

- Elegant product presentation
- Smooth shopping flow
- Admin-friendly management
- Production-ready architecture

The design emphasizes a matte-black luxury aesthetic inspired by modern skincare brands.

---

## Tech Stack

- Django 5
- PostgreSQL (SQLite for development)
- Django templates + custom CSS
- Modular app architecture

---

## Quick Start

### 1. Setup environment

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:

```env
SECRET_KEY=generate-secure-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

Generate key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Database setup

```bash
python manage.py migrate
python manage.py createsuperuser
```

(Optional) load sample data via Django shell.

### 4. Run server

```bash
python manage.py runserver
```

Visit:

```
http://localhost:8000
```

---

## Project Structure

```
vantor_project/
├── config/        # Django settings & routing
├── products/      # Catalog & product management
├── cart/          # Shopping cart logic
├── orders/        # Checkout & order handling
├── accounts/      # Authentication
├── templates/     # UI templates
├── static/        # CSS, JS, assets
└── manage.py
```

---

## Core Features

### Customer Experience

- Product catalog with galleries
- Session-based cart
- Checkout flow
- Account registration/login
- Order tracking

### Admin Tools

- Product & category management
- Image handling
- Inventory control
- Order workflow management

---

## Design System

**Palette**

- Matte black — primary
- Charcoal — depth
- Subtle gold — accents
- Soft off-white — background

**Typography**

- Cormorant Garamond (display)
- Inter (body)

Design goals:

- High whitespace
- Smooth transitions
- Clean luxury presentation
- Mobile-first layout

---

## Database Overview

**Products**

- Category
- Product
- ProductImage

**Orders**

- Order
- OrderItem

Order data is partially denormalized for performance and historical accuracy.

---

## Deployment Notes

Production checklist:

- Disable DEBUG
- Secure SECRET_KEY
- Use PostgreSQL
- Configure allowed hosts
- Collect static files

```bash
python manage.py collectstatic
gunicorn config.wsgi:application
```

Recommended stack:

- VPS or cloud hosting
- Managed PostgreSQL
- CDN/media storage (S3 or Cloudinary)

---

## Security

- CSRF protection
- ORM-based SQL safety
- Password hashing
- Production HTTPS support

---

## Scalability Ready

Architecture supports:

- Optimized database queries
- CDN integration
- API expansion
- Redis caching upgrades
- Async task pipelines

Future expansion ideas:

- Payment gateways
- Wishlist & reviews
- Advanced search
- Multi-currency support

---

## Testing

```bash
python manage.py test
```

---

## License

Proprietary platform for Vantor brand use.

---

## Credits

Built with Django and modern web standards.  
Inspired by global luxury skincare experiences.

---

**Built for scale. Designed for luxury. Made in Nepal.**
