# Vantor - Premium Skincare E-commerce Platform

## 🏗️ Project Architecture

A production-ready Django e-commerce application built with scalability, performance, and luxury UX in mind.

### **Tech Stack**
- **Backend**: Django 5.0.1
- **Database**: PostgreSQL (SQLite for development)
- **Frontend**: Django Templates + Custom CSS
- **Architecture**: Modular app structure with service layer pattern

### **Design Philosophy**
- **Matte black luxury aesthetic** with premium typography
- **Minimal, high-whitespace layouts** inspired by luxury brands
- **Mobile-first responsive design**
- **Performance-optimized** with query optimization and lazy loading

---

## 🚀 Quick Start Guide

### **Prerequisites**
- Python 3.10+
- PostgreSQL 14+ (for production) or SQLite (development)
- Git

### **Installation Steps**

#### 1. Clone or Download Project
```bash
cd vantor_project
```

#### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Environment Configuration
```bash
cp .env.example .env
```

Edit `.env` file:
```env
SECRET_KEY=your-secret-key-here-generate-new-one
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# For development, use SQLite (default)
# DATABASE_URL=sqlite:///db.sqlite3

# For production, use PostgreSQL
# DATABASE_URL=postgresql://username:password@localhost:5432/vantor_db
```

**Generate a secure SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### 5. Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

#### 6. Create Superuser (Admin Access)
```bash
python manage.py createsuperuser
```

Follow prompts to create admin account.

#### 7. Load Sample Data (Optional)
```bash
python manage.py shell
```

Then run:
```python
from products.models import Category, Product, ProductImage

# Create categories
skincare = Category.objects.create(
    name="Skincare",
    description="Premium skincare products"
)

# Create sample products
product = Product.objects.create(
    name="Himalayan Radiance Serum",
    category=skincare,
    description="A luxurious serum infused with Himalayan botanicals for radiant skin.",
    short_description="Radiance-boosting serum with natural ingredients",
    benefits="Brightens skin\nReduces fine lines\nHydrates deeply",
    how_to_use="Apply 2-3 drops to cleansed face morning and evening.",
    price=2500.00,
    stock_quantity=50,
    is_active=True,
    is_featured=True
)

print("Sample data created!")
exit()
```

#### 8. Run Development Server
```bash
python manage.py runserver
```

Visit: **http://localhost:8000**

---

## 📁 Project Structure

```
vantor_project/
├── config/                 # Project configuration
│   ├── settings.py        # Django settings
│   ├── urls.py            # Main URL routing
│   ├── wsgi.py            # WSGI config
│   └── asgi.py            # ASGI config
├── products/              # Product catalog app
│   ├── models.py          # Product, Category, ProductImage models
│   ├── views.py           # Product views (Home, List, Detail)
│   ├── admin.py           # Enhanced admin interface
│   └── urls.py            # Product URL routing
├── cart/                  # Shopping cart app
│   ├── cart.py            # Cart service class
│   ├── views.py           # Cart operations
│   └── context_processors.py
├── orders/                # Order management app
│   ├── models.py          # Order, OrderItem models
│   ├── views.py           # Checkout, order confirmation
│   ├── forms.py           # Order forms
│   └── admin.py           # Order admin interface
├── accounts/              # User authentication
│   ├── views.py           # Login, register, profile
│   ├── forms.py           # Auth forms
│   └── urls.py            # Account routing
├── templates/             # HTML templates
│   ├── base.html          # Base template
│   ├── products/          # Product templates
│   ├── cart/              # Cart templates
│   ├── orders/            # Order templates
│   └── accounts/          # Account templates
├── static/                # Static files
│   ├── css/
│   │   └── main.css       # Luxury design system
│   ├── js/
│   └── images/
├── media/                 # User-uploaded files
│   └── products/          # Product images
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore            # Git ignore rules
└── manage.py             # Django management script
```

---

## 🎨 Design System

### **Color Palette**
- **Primary**: Matte Black (`#0A0A0A`)
- **Secondary**: Charcoal (`#1A1A1A`)
- **Accent**: Subtle Gold (`#D4AF37`)
- **Background**: Off-White (`#F5F5F5`)

### **Typography**
- **Display**: Cormorant Garamond (luxury serif)
- **Body**: Inter (clean sans-serif)

### **UI Principles**
- High whitespace for breathing room
- Subtle hover transitions (400ms ease)
- Minimal borders and shadows
- Large, readable typography
- Mobile-first responsive grid

---

## 🔧 Admin Panel

Access the admin panel at: **http://localhost:8000/admin**

### **Admin Features**

#### Product Management
- ✅ Inline image management
- ✅ Stock tracking
- ✅ Featured/bestseller flags
- ✅ SEO fields (meta title, description)
- ✅ Bulk actions (mark as featured, out of stock)

#### Order Management
- ✅ Order status workflow (pending → processing → shipped → delivered)
- ✅ Customer information
- ✅ Order items with pricing snapshot
- ✅ Bulk status updates

#### Category Management
- ✅ Category with description and images
- ✅ Product count tracking

---

## 🛒 Core Features

### **Customer Features**
- ✅ Product browsing with filters
- ✅ Product detail pages with gallery
- ✅ Session-based shopping cart
- ✅ Checkout with order confirmation
- ✅ User registration and login
- ✅ Order history (for registered users)

### **Admin Features**
- ✅ Product CRUD operations
- ✅ Image management (multiple images per product)
- ✅ Order management and status tracking
- ✅ Inventory control
- ✅ Customer data access

---

## 📊 Database Schema

### **Products App**
```
Category
- name, slug, description
- image, is_active
- timestamps

Product
- name, slug, category
- description, short_description
- benefits, ingredients, how_to_use
- price, compare_at_price, stock_quantity
- is_active, is_featured, is_bestseller, is_new_arrival
- SEO fields, timestamps

ProductImage
- product, image, alt_text
- is_primary, order
- timestamp
```

### **Orders App**
```
Order
- order_number (UUID)
- user (optional), customer info (denormalized)
- shipping address
- status, pricing (snapshot)
- payment info, timestamps

OrderItem
- order, product_id (reference, not FK)
- product_name, product_slug (denormalized)
- price, quantity (snapshot)
```

---

## 🚀 Deployment Guide

### **Production Checklist**

#### 1. Environment Variables
```bash
DEBUG=False
SECRET_KEY=generate-strong-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:pass@localhost/db
```

#### 2. Static Files
```bash
python manage.py collectstatic
```

#### 3. Database Migration
```bash
python manage.py migrate --no-input
```

#### 4. Web Server (Gunicorn)
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

#### 5. Reverse Proxy (Nginx)
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /static/ {
        alias /path/to/staticfiles/;
    }

    location /media/ {
        alias /path/to/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### **Recommended Hosting**
- **Platform**: DigitalOcean, AWS, Heroku
- **Database**: Managed PostgreSQL
- **Media Storage**: AWS S3 or Cloudinary
- **CDN**: Cloudflare

---

## 🔐 Security Features

- ✅ CSRF protection enabled
- ✅ SQL injection prevention (ORM)
- ✅ XSS protection
- ✅ Secure password hashing (PBKDF2)
- ✅ HTTPS enforcement (production)
- ✅ Security headers (production)

---

## 📈 Scalability Considerations

### **Current Architecture Supports:**
- Database indexing on frequently queried fields
- Query optimization with `select_related` and `prefetch_related`
- Session-based cart (easily upgradeable to database-backed)
- Denormalized order data for performance
- Ready for CDN integration
- API-ready structure (easy to add DRF)

### **Future Enhancements:**
- Redis for session storage and caching
- Celery for async tasks (email notifications, image processing)
- Elasticsearch for advanced product search
- Multi-currency support
- Payment gateway integration (Stripe, Khalti)
- Wishlist functionality
- Product reviews and ratings

---

## 🧪 Testing

Run tests:
```bash
python manage.py test
```

---

## 🤝 Support

For issues or questions:
- Create an issue in the project repository
- Email: dev@vantor.com (placeholder)

---

## 📄 License

This project is a proprietary e-commerce platform for Vantor.

---

## 🙏 Credits

**Design & Development**: Built with Django and modern web standards
**Typography**: Google Fonts (Cormorant Garamond, Inter)
**Inspiration**: Luxury international skincare brands

---

**Built for scale. Designed for luxury. Made in Nepal. 🇳🇵**
