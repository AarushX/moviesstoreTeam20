from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review
from django.db.models import Count
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
    # Aggregate purchases per movie per city
    movie_counts = list(
        Item.objects
        .values(
            'movie__id',
            'movie__name',
            'order__city',
            'order__state',
            'order__country',
            'order__latitude',
            'order__longitude'
        )
        .annotate(count=Count('id'))
    )
    
    # Group by location to combine multiple movies at same location
    locations = {}
    movies_summary = {}  # Track all movies and their total purchases
    
    for item in movie_counts:
        if item['order__latitude'] and item['order__longitude']:
            # Create a location key
            loc_key = f"{item['order__latitude']},{item['order__longitude']}"
            
            if loc_key not in locations:
                locations[loc_key] = {
                    'latitude': item['order__latitude'],
                    'longitude': item['order__longitude'],
                    'city': item['order__city'],
                    'state': item['order__state'],
                    'country': item['order__country'],
                    'movies': [],
                    'total_purchases': 0
                }
            
            locations[loc_key]['movies'].append({
                'id': item['movie__id'],
                'name': item['movie__name'],
                'count': item['count']
            })
            locations[loc_key]['total_purchases'] += item['count']
            
            # Track movie summary
            movie_id = item['movie__id']
            if movie_id not in movies_summary:
                movies_summary[movie_id] = {
                    'id': movie_id,
                    'name': item['movie__name'],
                    'total_purchases': 0,
                    'locations': []
                }
            movies_summary[movie_id]['total_purchases'] += item['count']
            movies_summary[movie_id]['locations'].append({
                'city': item['order__city'],
                'state': item['order__state'],
                'country': item['order__country'],
                'latitude': item['order__latitude'],
                'longitude': item['order__longitude'],
                'count': item['count']
            })
    
    # Convert to lists for JSON serialization
    locations_list = list(locations.values())
    movies_list = sorted(movies_summary.values(), key=lambda x: x['total_purchases'], reverse=True)
    
    locations_json = json.dumps(locations_list, ensure_ascii=False)
    movies_json = json.dumps(movies_list, ensure_ascii=False)

    return render(
        request,
        'movies/rating_map.html',
        {
            'locations_json': locations_json,
            'movies_json': movies_json
        }
    )

