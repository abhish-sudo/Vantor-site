"""
Sample Data Loader for Vantor
Run this to populate the database with demo products
Usage: python manage.py shell < load_sample_data.py
"""

from products.models import Category, Product, ProductImage
from django.core.files import File
from decimal import Decimal

print("Loading sample data for Vantor...")

# Create Categories
print("\n Creating categories...")
skincare = Category.objects.get_or_create(
    name="Skincare",
    defaults={
        'description': 'Premium skincare formulations for radiant, healthy skin',
        'is_active': True
    }
)[0]

serums = Category.objects.get_or_create(
    name="Serums",
    defaults={
        'description': 'Concentrated treatments for targeted skin concerns',
        'is_active': True
    }
)[0]

moisturizers = Category.objects.get_or_create(
    name="Moisturizers",
    defaults={
        'description': 'Hydrating formulas for all skin types',
        'is_active': True
    }
)[0]

cleansers = Category.objects.get_or_create(
    name="Cleansers",
    defaults={
        'description': 'Gentle yet effective facial cleansers',
        'is_active': True
    }
)[0]

print(f"✓ Created {Category.objects.count()} categories")

# Create Products
print("\n Creating products...")

products_data = [
    {
        'name': 'Himalayan Radiance Serum',
        'category': serums,
        'description': 'A luxurious serum infused with rare Himalayan botanicals, designed to illuminate your complexion from within. This lightweight formula absorbs instantly, delivering potent antioxidants and vitamins deep into the skin.',
        'short_description': 'Illuminate your skin with Himalayan botanicals',
        'benefits': 'Brightens dull skin\nReduces appearance of dark spots\nBoosts natural radiance\nProvides deep hydration\nProtects against environmental damage',
        'ingredients': 'Aqua, Rhododendron Extract, Hyaluronic Acid, Vitamin C, Niacinamide, Glycerin',
        'how_to_use': 'Apply 2-3 drops to cleansed face morning and evening. Gently press into skin until fully absorbed. Follow with moisturizer.',
        'price': Decimal('2500.00'),
        'compare_at_price': Decimal('3200.00'),
        'stock_quantity': 50,
        'is_active': True,
        'is_featured': True,
        'is_bestseller': True,
        'is_new_arrival': False
    },
    {
        'name': 'Mountain Dew Hydrating Cream',
        'category': moisturizers,
        'description': 'Experience the purity of Himalayan glacier water in this deeply nourishing cream. Lightweight yet intensely hydrating, it creates a protective barrier while allowing your skin to breathe.',
        'short_description': 'Glacier water-infused hydration',
        'benefits': 'Provides 24-hour hydration\nStrengthens skin barrier\nSoothes irritated skin\nImproves skin elasticity\nNon-greasy formula',
        'ingredients': 'Glacier Water, Shea Butter, Ceramides, Peptides, Alpine Rose Extract',
        'how_to_use': 'Apply to cleansed face and neck morning and evening. Massage gently in upward motions until absorbed.',
        'price': Decimal('2200.00'),
        'stock_quantity': 45,
        'is_active': True,
        'is_featured': True,
        'is_bestseller': False,
        'is_new_arrival': True
    },
    {
        'name': 'Sacred Lotus Gentle Cleanser',
        'category': cleansers,
        'description': 'A gentle yet effective cleanser that respects your skin\'s delicate balance. Enriched with sacred lotus extract and rice water, it removes impurities while maintaining essential moisture.',
        'short_description': 'Gentle purification with sacred lotus',
        'benefits': 'Removes makeup and impurities\nMaintains skin pH balance\nDoesn\'t strip natural oils\nSoftens and smooths skin\nSuitable for sensitive skin',
        'ingredients': 'Rice Water, Lotus Extract, Coconut-derived Surfactants, Chamomile, Aloe Vera',
        'how_to_use': 'Wet face with lukewarm water. Massage a small amount onto skin in circular motions. Rinse thoroughly. Use morning and evening.',
        'price': Decimal('1800.00'),
        'stock_quantity': 60,
        'is_active': True,
        'is_featured': True,
        'is_bestseller': True,
        'is_new_arrival': False
    },
    {
        'name': 'Yarsagumba Youth Revival Serum',
        'category': serums,
        'description': 'Harness the legendary power of Yarsagumba (Cordyceps) in this age-defying serum. This rare ingredient, combined with cutting-edge peptides, works to restore firmness and reduce visible signs of aging.',
        'short_description': 'Age-defying power of Yarsagumba',
        'benefits': 'Reduces fine lines and wrinkles\nImproves skin firmness\nBoosts collagen production\nEnhances skin texture\nPromotes cellular renewal',
        'ingredients': 'Cordyceps Extract, Retinol, Peptide Complex, Vitamin E, Squalane',
        'how_to_use': 'Apply 3-4 drops to cleansed skin in the evening. Start with 2-3 times per week, gradually increasing to nightly use.',
        'price': Decimal('3500.00'),
        'compare_at_price': Decimal('4200.00'),
        'stock_quantity': 30,
        'is_active': True,
        'is_featured': False,
        'is_bestseller': False,
        'is_new_arrival': True
    },
    {
        'name': 'Everest Cloud Cream',
        'category': moisturizers,
        'description': 'Lightweight as mountain clouds, powerful as the peaks themselves. This whipped cream delivers intense hydration without heaviness, perfect for Nepal\'s diverse climate.',
        'short_description': 'Cloud-light intense hydration',
        'benefits': 'Ultra-lightweight texture\nIntense hydration\nControls excess oil\nRefines pores\nMatte finish',
        'ingredients': 'Snow Mushroom, Niacinamide, Zinc PCA, Green Tea Extract, Hyaluronic Acid',
        'how_to_use': 'Apply a small amount to face after cleansing and toning. Use morning and/or evening as needed.',
        'price': Decimal('2400.00'),
        'stock_quantity': 40,
        'is_active': True,
        'is_featured': False,
        'is_bestseller': True,
        'is_new_arrival': False
    },
    {
        'name': 'Rhododendron Gentle Exfoliating Cleanser',
        'category': cleansers,
        'description': 'Nepal\'s national flower lends its gentle exfoliating properties to this luxurious cleanser. Micro rice powder provides physical exfoliation while botanical enzymes work at a cellular level.',
        'short_description': 'Dual-action exfoliating cleanser',
        'benefits': 'Gentle daily exfoliation\nUnclogs pores\nBrightens complexion\nSmoothes texture\nPrepares skin for treatments',
        'ingredients': 'Rhododendron Extract, Rice Powder, Papaya Enzymes, Jojoba Beads, Calendula',
        'how_to_use': 'Use 2-3 times per week. Massage onto damp skin for 30 seconds, avoiding eye area. Rinse with lukewarm water.',
        'price': Decimal('1950.00'),
        'stock_quantity': 55,
        'is_active': True,
        'is_featured': False,
        'is_bestseller': False,
        'is_new_arrival': True
    }
]

for product_data in products_data:
    product, created = Product.objects.get_or_create(
        name=product_data['name'],
        defaults=product_data
    )
    if created:
        print(f"✓ Created: {product.name}")
    else:
        print(f"  Skipped (exists): {product.name}")

print(f"\n✓ Total products in database: {Product.objects.count()}")

print("\n Sample data loaded successfully!")
print("\n Next steps:")
print("  1. Add product images through the admin panel")
print("  2. Visit http://localhost:8000 to see your store")
print("  3. Admin panel: http://localhost:8000/admin")
