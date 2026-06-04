from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator
from datetime import timedelta, date
from decimal import Decimal
import json
import uuid

from .models import Product, Category, Supplier, Sale, SaleItem, StockMovement
from .forms import ProductForm, CategoryForm, SupplierForm, StockAdjustmentForm, SaleForm, ProductSearchForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Invalid username or password.')
    return render(request, 'store/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    today = date.today()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    total_products = Product.objects.filter(is_active=True).count()
    total_categories = Category.objects.count()
    low_stock = Product.objects.filter(is_active=True, stock_quantity__lte=F('reorder_level')).count()
    out_of_stock = Product.objects.filter(is_active=True, stock_quantity=0).count()

    today_sales = Sale.objects.filter(created_at__date=today)
    today_revenue = today_sales.aggregate(total=Sum('total'))['total'] or 0
    today_orders = today_sales.count()

    weekly_revenue = Sale.objects.filter(created_at__date__gte=week_ago).aggregate(total=Sum('total'))['total'] or 0
    monthly_revenue = Sale.objects.filter(created_at__date__gte=month_ago).aggregate(total=Sum('total'))['total'] or 0

    total_stock_value = Product.objects.filter(is_active=True).aggregate(
        val=Sum(F('stock_quantity') * F('cost_price'))
    )['val'] or 0

    recent_sales = Sale.objects.select_related('cashier').prefetch_related('items')[:8]
    low_stock_products = Product.objects.filter(
        is_active=True, stock_quantity__lte=F('reorder_level')
    ).select_related('category').order_by('stock_quantity')[:8]

    # Sales chart data (last 7 days)
    chart_labels = []
    chart_data = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        rev = Sale.objects.filter(created_at__date=d).aggregate(total=Sum('total'))['total'] or 0
        chart_labels.append(d.strftime('%a'))
        chart_data.append(float(rev))

    # Top products
    top_products = SaleItem.objects.values('product_name').annotate(
        total_qty=Sum('quantity'), total_rev=Sum('total_price')
    ).order_by('-total_rev')[:5]

    context = {
        'total_products': total_products,
        'total_categories': total_categories,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
        'today_revenue': today_revenue,
        'today_orders': today_orders,
        'weekly_revenue': weekly_revenue,
        'monthly_revenue': monthly_revenue,
        'total_stock_value': total_stock_value,
        'recent_sales': recent_sales,
        'low_stock_products': low_stock_products,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        'top_products': top_products,
    }
    return render(request, 'store/dashboard.html', context)


# ─── Products ─────────────────────────────────────────────────────────────────

@login_required
def product_list(request):
    form = ProductSearchForm(request.GET)
    products = Product.objects.select_related('category', 'supplier').all()

    if form.is_valid():
        q = form.cleaned_data.get('query')
        cat = form.cleaned_data.get('category')
        if q:
            products = products.filter(Q(name__icontains=q) | Q(sku__icontains=q) | Q(barcode__icontains=q))
        if cat:
            products = products.filter(category=cat)

    status_filter = request.GET.get('status', '')
    if status_filter == 'low':
        products = products.filter(stock_quantity__lte=F('reorder_level'), stock_quantity__gt=0)
    elif status_filter == 'out':
        products = products.filter(stock_quantity=0)
    elif status_filter == 'active':
        products = products.filter(is_active=True)

    paginator = Paginator(products, 20)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'store/products.html', {'products': page, 'form': form, 'status_filter': status_filter})


@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            if product.stock_quantity > 0:
                StockMovement.objects.create(
                    product=product, movement_type='in',
                    quantity=product.stock_quantity, previous_quantity=0,
                    new_quantity=product.stock_quantity,
                    reason='Initial stock', performed_by=request.user
                )
            messages.success(request, f'Product "{product.name}" created successfully!')
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'store/product_form.html', {'form': form, 'title': 'Add Product'})


@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Product "{product.name}" updated!')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'store/product_form.html', {'form': form, 'product': product, 'title': 'Edit Product'})


@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    movements = product.movements.select_related('performed_by').order_by('-created_at')[:20]
    return render(request, 'store/product_detail.html', {'product': product, 'movements': movements})


@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'"{name}" deleted.')
        return redirect('product_list')
    return render(request, 'store/confirm_delete.html', {'object': product, 'type': 'Product'})


@login_required
def stock_adjust(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = StockAdjustmentForm(request.POST)
        if form.is_valid():
            mv_type = form.cleaned_data['movement_type']
            qty = form.cleaned_data['quantity']
            reason = form.cleaned_data['reason']
            prev = product.stock_quantity

            if mv_type == 'in':
                product.stock_quantity += qty
            elif mv_type == 'out':
                if qty > product.stock_quantity:
                    messages.error(request, 'Not enough stock!')
                    return redirect('stock_adjust', pk=pk)
                product.stock_quantity -= qty
            else:
                product.stock_quantity = qty

            product.save()
            StockMovement.objects.create(
                product=product, movement_type=mv_type,
                quantity=qty, previous_quantity=prev,
                new_quantity=product.stock_quantity,
                reason=reason, performed_by=request.user
            )
            messages.success(request, f'Stock updated for "{product.name}".')
            return redirect('product_detail', pk=pk)
    else:
        form = StockAdjustmentForm()
    return render(request, 'store/stock_adjust.html', {'form': form, 'product': product})


# ─── Categories ───────────────────────────────────────────────────────────────

@login_required
def category_list(request):
    categories = Category.objects.annotate(product_count=Count('products')).order_by('name')
    return render(request, 'store/categories.html', {'categories': categories})


@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created!')
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'store/category_form.html', {'form': form, 'title': 'Add Category'})


@login_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated!')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'store/category_form.html', {'form': form, 'title': 'Edit Category'})


@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted.')
        return redirect('category_list')
    return render(request, 'store/confirm_delete.html', {'object': category, 'type': 'Category'})


# ─── Suppliers ────────────────────────────────────────────────────────────────

@login_required
def supplier_list(request):
    suppliers = Supplier.objects.annotate(product_count=Count('product')).order_by('name')
    return render(request, 'store/suppliers.html', {'suppliers': suppliers})


@login_required
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier added!')
            return redirect('supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'store/supplier_form.html', {'form': form, 'title': 'Add Supplier'})


@login_required
def supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier updated!')
            return redirect('supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'store/supplier_form.html', {'form': form, 'title': 'Edit Supplier'})


@login_required
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.delete()
        messages.success(request, 'Supplier deleted.')
        return redirect('supplier_list')
    return render(request, 'store/confirm_delete.html', {'object': supplier, 'type': 'Supplier'})


# ─── Sales / POS ──────────────────────────────────────────────────────────────

@login_required
@ensure_csrf_cookie
def pos(request):
    categories = Category.objects.all()
    products = Product.objects.filter(is_active=True, stock_quantity__gt=0).select_related('category')
    return render(request, 'store/pos.html', {'categories': categories, 'products': products})


@login_required
def create_sale(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        items = data.get('items', [])
        if not items:
            return JsonResponse({'error': 'No items in cart'}, status=400)

        subtotal = 0
        sale_items = []
        for item in items:
            product = get_object_or_404(Product, pk=item['id'])
            qty = int(item['qty'])
            if product.stock_quantity < qty:
                return JsonResponse({'error': f'Not enough stock for {product.name}'}, status=400)
            item_total = product.selling_price * qty
            subtotal += item_total
            sale_items.append({'product': product, 'qty': qty, 'price': product.selling_price, 'total': item_total})

        discount = Decimal(str(data.get('discount', 0)))
        total = subtotal - discount
        invoice = f"INV-{timezone.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"

        sale = Sale.objects.create(
            invoice_number=invoice,
            cashier=request.user,
            payment_method=data.get('payment_method', 'cash'),
            subtotal=subtotal,
            discount=discount,
            total=total,
            customer_name=data.get('customer_name', ''),
            notes=data.get('notes', '')
        )

        for si in sale_items:
            SaleItem.objects.create(
                sale=sale, product=si['product'],
                product_name=si['product'].name,
                quantity=si['qty'], unit_price=si['price'], total_price=si['total']
            )
            prev = si['product'].stock_quantity
            si['product'].stock_quantity -= si['qty']
            si['product'].save()
            StockMovement.objects.create(
                product=si['product'], movement_type='out',
                quantity=si['qty'], previous_quantity=prev,
                new_quantity=si['product'].stock_quantity,
                reason=f'Sale {invoice}', reference=invoice,
                performed_by=request.user
            )

        return JsonResponse({'success': True, 'invoice': invoice, 'total': float(total), 'sale_id': sale.id})

    return JsonResponse({'error': 'Invalid method'}, status=405)


@login_required
def sale_list(request):
    sales = Sale.objects.select_related('cashier').prefetch_related('items').order_by('-created_at')
    q = request.GET.get('q', '')
    if q:
        sales = sales.filter(Q(invoice_number__icontains=q) | Q(customer_name__icontains=q))
    paginator = Paginator(sales, 20)
    page = paginator.get_page(request.GET.get('page'))
    total_revenue = sales.aggregate(total=Sum('total'))['total'] or 0
    return render(request, 'store/sales.html', {'sales': page, 'q': q, 'total_revenue': total_revenue})


@login_required
def sale_detail(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    return render(request, 'store/sale_detail.html', {'sale': sale})


# ─── API ──────────────────────────────────────────────────────────────────────

@login_required
def print_receipt(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    autoprint = request.GET.get('autoprint', '0') == '1'
    return render(request, 'store/print_receipt.html', {'sale': sale, 'autoprint': autoprint})


@login_required
def api_products(request):
    cat_id = request.GET.get('category')
    products = Product.objects.filter(is_active=True, stock_quantity__gt=0)
    if cat_id:
        products = products.filter(category_id=cat_id)
    data = [{
        'id': p.id, 'name': p.name,
        'price': float(p.selling_price),
        'stock': p.stock_quantity, 'unit': p.unit,
        'category': p.category.name if p.category else '',
    } for p in products]
    return JsonResponse({'products': data})
