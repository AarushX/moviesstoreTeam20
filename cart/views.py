from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from movies.models import Movie
from .utils import calculate_cart_total
from .models import Order, Item
from django.contrib.auth.decorators import login_required

def index(request):
    cart_total = 0
    movies_in_cart = []
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())
    if (movie_ids != []):
        movies_in_cart = Movie.objects.filter(id__in=movie_ids)
        cart_total = calculate_cart_total(cart,
            movies_in_cart)
    template_data = {}
    template_data['title'] = 'Cart'
    template_data['movies_in_cart'] = movies_in_cart
    template_data['cart_total'] = cart_total
    return render(request, 'cart/index.html',
        {'template_data': template_data})

def add(request, id):
    get_object_or_404(Movie, id=id)
    cart = request.session.get('cart', {})
    cart[id] = request.POST['quantity']
    request.session['cart'] = cart
    return redirect('cart.index')

def clear(request):
    request.session['cart'] = {}
    return redirect('cart.index')

@login_required
def purchase(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        movie_ids = list(cart.keys())
        if not movie_ids:
            return redirect('cart.index')

        # Get location info from form
        city = request.POST.get('city')
        state = request.POST.get('state')
        country = request.POST.get('country', 'USA')

        movies_in_cart = Movie.objects.filter(id__in=movie_ids)
        cart_total = calculate_cart_total(cart, movies_in_cart)

        # Create Order with location info
        order = Order(
            user=request.user,
            total=cart_total,
            city=city,
            state=state,
            country=country
        )
        order.save()  # save() will trigger automatic latitude/longitude

        # Create Item objects
        for movie in movies_in_cart:
            Item.objects.create(
                movie=movie,
                price=movie.price,
                order=order,
                quantity=cart[str(movie.id)]
            )

        # Clear cart
        request.session['cart'] = {}

        template_data = {
            'title': 'Purchase confirmation',
            'order_id': order.id
        }
        return render(request, 'cart/purchase.html', {'template_data': template_data})

    # If GET request, redirect to cart page
    return redirect('cart.index')