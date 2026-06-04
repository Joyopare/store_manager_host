# 🏪 StoreFlow — Store Management System

A beautiful, professional Django store management system with POS, inventory, sales tracking, and more.

---

## 🚀 Quick Setup

### 1. Install Requirements
```bash
pip install -r requirements.txt
```

### 2. Run Migrations
```bash
python manage.py migrate
```

### 3. Seed Sample Data (optional but recommended)
```bash
python manage.py seed_data
```
This creates:
- **Admin user**: `admin` / `admin123`
- 10 product categories (Water, Drinks, Snacks, etc.)
- 30 sample products with realistic prices
- 2 suppliers

### 4. Start the Server
```bash
python manage.py runserver
```

### 5. Open in Browser
```
http://127.0.0.1:8000
```

---

## 🔑 Default Login
| Username | Password |
|----------|----------|
| admin    | admin123 |

---

## ✨ Features

### 📊 Dashboard
- Real-time revenue stats (today, weekly, monthly)
- Interactive 7-day revenue chart
- Low stock alerts
- Top selling products
- Recent sales feed

### 🛒 Point of Sale (POS)
- Fast product search and category filtering
- Add/remove items from cart
- Adjust quantities
- Apply discounts
- Multiple payment methods (Cash, Card, Mobile Money)
- Auto-updates stock after each sale

### 📦 Inventory Management
- Add/edit/delete products
- Product images
- Cost & selling price tracking
- Profit margin calculation
- Stock quantity management
- Reorder level alerts
- Stock movement history

### 🏷️ Categories
- Organize products by category
- Custom emoji icons
- Product counts per category

### 🚚 Suppliers
- Manage supplier contacts
- Link products to suppliers

### 💳 Sales History
- Full sales records with invoices
- Search by invoice or customer
- Detailed sale receipts
- Payment method tracking

---

## 🛠️ Admin Panel
Access Django's built-in admin at:
```
http://127.0.0.1:8000/admin/
```

---

## 📁 Project Structure
```
store_manager/
├── manage.py
├── requirements.txt
├── README.md
├── db.sqlite3          ← created after migrate
├── media/              ← product images
├── store_manager/      ← Django project settings
│   ├── settings.py
│   └── urls.py
└── store/              ← Main application
    ├── models.py       ← Database models
    ├── views.py        ← Business logic
    ├── urls.py         ← URL routing
    ├── forms.py        ← Form definitions
    ├── templates/
    │   └── store/      ← HTML templates
    └── management/
        └── commands/
            └── seed_data.py
```

---

## 💡 Tips
- Use `python manage.py createsuperuser` to create additional admin users
- Change `SECRET_KEY` in `settings.py` before deploying to production
- Set `DEBUG = False` in production
- Configure a proper database (PostgreSQL) for production use
