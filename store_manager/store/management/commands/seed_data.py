from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import Category, Supplier, Product
from decimal import Decimal


class Command(BaseCommand):
    help = 'Seed the database with sample data'

    def handle(self, *args, **kwargs):
        # Admin user
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@store.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('✅ Created admin user (admin/admin123)'))

        # Categories
        cats_data = [
            ('Water & Beverages', 'water-beverages', '💧', 'All water and beverage products'),
            ('Soft Drinks', 'soft-drinks', '🥤', 'Carbonated and non-carbonated soft drinks'),
            ('Energy Drinks', 'energy-drinks', '⚡', 'Energy and sports drinks'),
            ('Snacks', 'snacks', '🍟', 'Chips, biscuits and snack foods'),
            ('Dairy', 'dairy', '🥛', 'Milk, yogurt and dairy products'),
            ('Confectionery', 'confectionery', '🍬', 'Sweets, chocolates and candies'),
            ('Canned Foods', 'canned-foods', '🥫', 'Canned and preserved foods'),
            ('Personal Care', 'personal-care', '🧴', 'Soaps, shampoos and personal care'),
            ('Household', 'household', '🧹', 'Cleaning and household items'),
            ('Tobacco', 'tobacco', '🚬', 'Cigarettes and tobacco products'),
        ]
        cats = {}
        for name, slug, icon, desc in cats_data:
            cat, _ = Category.objects.get_or_create(slug=slug, defaults={'name': name, 'icon': icon, 'description': desc})
            cats[slug] = cat

        # Supplier
        sup, _ = Supplier.objects.get_or_create(
            name='Ghana Beverages Ltd',
            defaults={'contact_person': 'Kwame Asante', 'phone': '+233 20 123 4567', 'email': 'supply@gbl.com'}
        )
        sup2, _ = Supplier.objects.get_or_create(
            name='Accra General Supplies',
            defaults={'contact_person': 'Ama Boateng', 'phone': '+233 24 987 6543', 'email': 'info@ags.com'}
        )

        # Products
        products = [
            # Water
            ('Voltic Water 500ml', 'water-beverages', 'VLT-500', Decimal('0.80'), Decimal('1.50'), 200, 30, 'bottle', sup),
            ('Voltic Water 1.5L', 'water-beverages', 'VLT-1500', Decimal('1.50'), Decimal('3.00'), 120, 20, 'bottle', sup),
            ('Voltic Water 5L', 'water-beverages', 'VLT-5000', Decimal('4.00'), Decimal('7.00'), 60, 10, 'bottle', sup),
            ('Ice Cool Water 500ml', 'water-beverages', 'ICW-500', Decimal('0.60'), Decimal('1.20'), 180, 25, 'bottle', sup),
            ('Aqua Pure 1L', 'water-beverages', 'AQP-1000', Decimal('1.20'), Decimal('2.50'), 90, 15, 'bottle', sup),
            # Soft Drinks
            ('Coca-Cola 500ml', 'soft-drinks', 'CCL-500', Decimal('2.50'), Decimal('5.00'), 150, 20, 'bottle', sup),
            ('Coca-Cola 330ml Can', 'soft-drinks', 'CCL-330C', Decimal('2.20'), Decimal('4.50'), 100, 15, 'can', sup),
            ('Pepsi 500ml', 'soft-drinks', 'PPS-500', Decimal('2.30'), Decimal('4.50'), 80, 15, 'bottle', sup),
            ('Fanta Orange 500ml', 'soft-drinks', 'FNT-ORG-500', Decimal('2.30'), Decimal('4.50'), 90, 15, 'bottle', sup),
            ('Sprite 500ml', 'soft-drinks', 'SPT-500', Decimal('2.30'), Decimal('4.50'), 70, 10, 'bottle', sup),
            ('Malta Guinness 330ml', 'soft-drinks', 'MLT-330', Decimal('2.00'), Decimal('4.00'), 60, 10, 'can', sup),
            ('Alvaro Pineapple 330ml', 'soft-drinks', 'ALV-PNP-330', Decimal('2.50'), Decimal('5.00'), 50, 8, 'can', sup),
            # Energy Drinks
            ('Power Horse 250ml', 'energy-drinks', 'PWH-250', Decimal('3.00'), Decimal('6.00'), 40, 10, 'can', sup),
            ('Red Bull 250ml', 'energy-drinks', 'RDB-250', Decimal('5.00'), Decimal('10.00'), 30, 5, 'can', sup),
            ('Rush Energy 250ml', 'energy-drinks', 'RSH-250', Decimal('2.50'), Decimal('5.00'), 45, 8, 'can', sup),
            # Snacks
            ('Pringles Original 165g', 'snacks', 'PRN-ORI-165', Decimal('8.00'), Decimal('15.00'), 25, 5, 'pack', sup2),
            ('Lays Classic 75g', 'snacks', 'LYS-CLS-75', Decimal('3.50'), Decimal('7.00'), 60, 10, 'pack', sup2),
            ('Biscuit Cabin 200g', 'snacks', 'BIS-CAB-200', Decimal('2.00'), Decimal('4.00'), 80, 15, 'pack', sup2),
            ('Digestive Biscuits 400g', 'snacks', 'DIG-BIS-400', Decimal('5.00'), Decimal('10.00'), 40, 8, 'pack', sup2),
            # Dairy
            ('Peak Milk 170g Tin', 'dairy', 'PMK-170T', Decimal('5.50'), Decimal('10.00'), 50, 10, 'piece', sup2),
            ('Fan Yogo Strawberry', 'dairy', 'FNY-STR', Decimal('1.50'), Decimal('3.00'), 30, 5, 'piece', sup),
            ('Nunu Yogurt 500ml', 'dairy', 'NNU-500', Decimal('4.00'), Decimal('8.00'), 20, 5, 'bottle', sup),
            # Confectionery
            ('Mentos Roll Mint', 'confectionery', 'MNT-ROLL-MINT', Decimal('1.00'), Decimal('2.00'), 100, 20, 'piece', sup2),
            ('Twix Bar', 'confectionery', 'TWX-BAR', Decimal('3.00'), Decimal('6.00'), 40, 8, 'piece', sup2),
            ('Kitkat 4-Finger', 'confectionery', 'KKT-4F', Decimal('2.50'), Decimal('5.00'), 50, 10, 'piece', sup2),
            # Canned Foods
            ('Titus Sardines 125g', 'canned-foods', 'TTS-125', Decimal('4.00'), Decimal('8.00'), 60, 10, 'piece', sup2),
            ('Geisha Sardines 155g', 'canned-foods', 'GIS-155', Decimal('3.50'), Decimal('7.00'), 70, 12, 'piece', sup2),
            ('Nido Corn Beef 340g', 'canned-foods', 'NCB-340', Decimal('12.00'), Decimal('22.00'), 30, 5, 'piece', sup2),
            # Personal Care
            ('Key Soap Bar 200g', 'personal-care', 'KEY-SB-200', Decimal('2.00'), Decimal('4.00'), 100, 20, 'piece', sup2),
            ('Vaseline Lotion 400ml', 'personal-care', 'VAS-400', Decimal('15.00'), Decimal('28.00'), 30, 5, 'bottle', sup2),
        ]

        count = 0
        for name, cat_slug, sku, cost, price, stock, reorder, unit, supplier in products:
            if not Product.objects.filter(sku=sku).exists():
                Product.objects.create(
                    name=name, category=cats[cat_slug], supplier=supplier,
                    sku=sku, cost_price=cost, selling_price=price,
                    stock_quantity=stock, reorder_level=reorder, unit=unit
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f'✅ Created {count} products'))
        self.stdout.write(self.style.SUCCESS('🎉 Database seeded! Login: admin / admin123'))
