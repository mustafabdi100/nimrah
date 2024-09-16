from django.shortcuts import render, get_object_or_404,redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from .models import Product, Review, Category,ProductSize, CartItem,Order,OrderItem
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import CheckoutForm
from decimal import Decimal


def get_parent_categories():
    return Category.objects.filter(parent=None)

def home(request):
  # Get all featured products
    featured_products = Product.objects.filter(is_featured=True).order_by('-id')
    best_seller_products = Product.objects.filter(is_best_seller=True).order_by('id')
    categories = Category.objects.filter(parent=None)
    
    # Get the Supplements category
    supplements_category = Category.objects.filter(name='Supplements').first()
    
    # Get all products from the Supplements category and its descendants
    if supplements_category:
        supplement_products = Product.objects.filter(
            category__in=supplements_category.get_descendants(include_self=True)
        )
    else:
        supplement_products = []

    context = {
        'categories': categories,
        'supplement_products': supplement_products,
        'featured_products': featured_products,
        'best_seller_products': best_seller_products,
    }
    
    
    return render(request, 'shop/home.html', context)

def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category__in=category.get_descendants(include_self=True))
    categories = get_parent_categories()
    return render(request, 'shop/category_products.html', {
        'category': category,
        'products': products,
        'categories': categories
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    product_sizes = product.product_sizes.all().order_by('price')
    reviews = product.reviews.all().order_by('-created_at')
    categories = get_parent_categories()
    
    # Get related products from the same category or its parent categories
    category_ids = [product.category.id] + list(product.category.get_ancestors().values_list('id', flat=True))
    related_products = Product.objects.filter(
        Q(category__id__in=category_ids) | Q(category__parent__id__in=category_ids)
    ).exclude(id=product.id).distinct().order_by('?')[:3]
    
    return render(request, 'shop/product_detail.html', {
        'product': product,
        'product_sizes': product_sizes,
        'reviews': reviews,
        'categories': categories,
        'related_products': related_products,
    })
  

@require_POST
def submit_review(request, slug):
    product = get_object_or_404(Product, slug=slug)
    data = json.loads(request.body)
    
    review = Review.objects.create(
        product=product,
        user_name=data['reviewerName'],
        user_email=data['reviewerEmail'],
        rating=data['rating'],
        text=data['reviewText']
    )
    
    return JsonResponse({
        'success': True,
        'review': {
            'rating': review.rating,
            'text': review.text,
            'created_at': review.created_at.isoformat(),
            'user_name': review.user_name,
        }
    })

@require_POST
def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    product_size_id = request.POST.get('size')
    quantity = int(request.POST.get('quantity', 1))

    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    if product_size_id:
        product_size = get_object_or_404(ProductSize, id=product_size_id)
        cart_item, created = CartItem.objects.get_or_create(
            session_key=session_key,
            product=product,
            product_size=product_size,
            defaults={'quantity': quantity}
        )
    else:
        cart_item, created = CartItem.objects.get_or_create(
            session_key=session_key,
            product=product,
            product_size=None,
            defaults={'quantity': quantity}
        )

    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    # Get the updated cart count
    cart_count = sum(item.quantity for item in CartItem.objects.filter(session_key=session_key))

    messages.success(request, f"{product.name} added to your cart.")
    
    # Redirect with updated cart count in session
    request.session['cart_count'] = cart_count
    return redirect('product_detail', slug=slug)


@require_POST
def remove_from_cart(request, item_id):
    session_key = request.session.session_key
    cart_item = get_object_or_404(CartItem, id=item_id, session_key=session_key)
    cart_item.delete()

    # Recalculate the cart count after removing the item
    new_cart_count = sum(item.quantity for item in CartItem.objects.filter(session_key=session_key))
    request.session['cart_count'] = new_cart_count

    messages.success(request, "Item removed from your cart.")
    return redirect('view_cart')


def view_cart(request):
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key
    cart_items = CartItem.objects.filter(session_key=session_key)
    
    total_price = sum(item.total_price for item in cart_items)
    cart_count = sum(item.quantity for item in cart_items)
    
    # Update the session cart count to ensure it is always accurate
    request.session['cart_count'] = cart_count

    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'cart_count': cart_count,
    })



def search(request):
    query = request.GET.get('q')
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()
    else:
        products = Product.objects.all()

    categories = Category.objects.filter(level=0)  # Get only root categories
    return render(request, 'shop/search_results.html', {
        'products': products,
        'query': query,
        'categories': categories
    })

def checkout(request):
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key
    cart_items = CartItem.objects.filter(session_key=session_key)
    
    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('view_cart')
    
    total_price = sum(item.total_price for item in cart_items)  # total_price is a Decimal
    shipping_price = Decimal('300.00')  # Define shipping_price as Decimal
    grand_total = total_price + shipping_price  # This will now work correctly

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Save the order
            order = form.save(commit=False)
            order.total_price = grand_total
            order.shipping_price = shipping_price
            order.save()

            # Save order items
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_size=item.product_size,
                    quantity=item.quantity,
                    price=item.total_price
                )

            # Clear the cart
            cart_items.delete()

            # Reset cart count in the session to 0
            request.session['cart_count'] = 0

            # Redirect to a success page
            return render(request, 'shop/order_success.html', {'order': order})
    else:
        form = CheckoutForm()
    
    return render(request, 'shop/checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'total_price': total_price,
        'shipping_price': shipping_price,
        'grand_total': grand_total,
    })
