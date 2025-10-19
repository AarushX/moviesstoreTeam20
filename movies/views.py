from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review
from django.db.models import Sum
from cart.models import Order, Item 
from django.contrib.auth.decorators import login_required
import json

# Defining the movie function
def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()
    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html',
                  {'template_data': template_data})
# Create your views here.

# Defining the views show function
def show(request, id): 
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie)
    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    return render(request, 'movies/show.html', {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment']!= '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html', {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id,
        user=request.user)
    review.delete()
    return redirect('movies.show', id=id)


def rating_map(request):
    # Aggregate purchases by city and movie using total quantity
    purchases = (
        Item.objects
        .values('order__city', 'order__latitude', 'order__longitude', 'movie__name')
        .annotate(total_quantity=Sum('quantity'))
    )

    # Keep only the most purchased movie per city
    city_popular = {}
    for p in purchases:
        city_key = (p['order__latitude'], p['order__longitude'], p['order__city'])
        if city_key not in city_popular or p['total_quantity'] > city_popular[city_key]['total_quantity']:
            city_popular[city_key] = {
                'movie_name': p['movie__name'],
                'total_quantity': p['total_quantity'],
                'latitude': p['order__latitude'],
                'longitude': p['order__longitude'],
                'city': p['order__city']
            }

    # Only include entries with valid coordinates
    city_popular_list = [c for c in city_popular.values() if c['latitude'] and c['longitude']]
    city_popular_json = json.dumps(city_popular_list, ensure_ascii=False)

    return render(request, 'movies/rating_map.html', {'movie_counts_json': city_popular_json})

