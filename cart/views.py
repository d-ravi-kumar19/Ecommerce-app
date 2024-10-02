from django.shortcuts import render, get_object_or_404, redirect
from .models import Cart, CartItem
from products.models import Product
from django.views.decorators.http import require_POST
from django.http import JsonResponse

@require_POST
def cart_add(request, product_id):
    cart_id = request.session.get("cart_id")

    # Fetch the cart or create a new one if it doesn't exist
    if cart_id:
        cart, created = Cart.objects.get_or_create(id=cart_id)
    else:
        cart = Cart.objects.create()
        request.session['cart_id'] = cart.id
    
    product = get_object_or_404(Product, id=product_id)
    
    # Get or create the CartItem
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    # Increment quantity if the item was already in the cart
    if not created:
        cart_item.quantity += 1

    cart_item.save()

    response_data = {
        "success": True,
        "message": f"Added {product.name} to cart",
        "quantity": cart_item.quantity  # Include quantity in the response
    }        

    return JsonResponse(response_data)

def cart_detail(request):
    cart_id = request.session.get('cart_id')
    cart = None

    if cart_id:
        cart = get_object_or_404(Cart, id=cart_id)
    if not cart or not cart.items.exists():
        cart = None
    return render(request, 'cart/detail.html', {"cart": cart})

# def cart_remove(request, product_id):
#     cart_id = request.session.get('cart_id')
#     cart = get_object_or_404(Cart,id = cart_id )
#     item = get_object_or_404(CartItem,id = product_id, cart = cart )
#     item.delete()

#     return redirect("cart:cart_detail")

@require_POST
def cart_remove(request, product_id):
    cart_id = request.session.get('cart_id')

    if not cart_id:
        # If there is no cart_id in the session, redirect to the cart detail or show an error
        return redirect("cart:cart_detail")

    cart = get_object_or_404(Cart, id=cart_id)
    
    # Attempt to get the CartItem
    try:
        item = get_object_or_404(CartItem, id=product_id, cart=cart)
        item.delete()
    except CartItem.DoesNotExist:
        # Handle the case where the CartItem does not exist
        return JsonResponse({'success': False, 'message': 'Item not found in cart'}, status=404)

    return redirect("cart:cart_detail")