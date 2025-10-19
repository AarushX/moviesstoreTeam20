from django.db import models
from django.contrib.auth.models import User
from movies.models import Movie
from .geocoding import geocode_address

class Order(models.Model):
    id = models.AutoField(primary_key=True)
    total = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User,
        on_delete=models.CASCADE)
    city = models.CharField(max_length=100, blank=True, null=True, help_text="City of purchase")
    state = models.CharField(max_length=100, blank=True, null=True, help_text="State/province of purchase")
    country = models.CharField(max_length=100, default='USA', help_text="Country of purchase")
    latitude = models.FloatField(blank=True, null=True, help_text="Latitude of purchase location")
    longitude = models.FloatField(blank=True, null=True, help_text="Longitude of purchase location")
    
    def __str__(self):
        return str(self.id) + ' - ' + self.user.username
    
    def save(self, *args, **kwargs):
        # Only try geocoding if lat/lon not already set and city exists
        if (not self.latitude or not self.longitude) and self.city:
            coordinates = geocode_address(self.city, self.state, self.country)
            if coordinates:
                self.latitude, self.longitude = coordinates

        super().save(*args, **kwargs)

class Item(models.Model):
    id = models.AutoField(primary_key=True)
    price = models.IntegerField()
    quantity = models.IntegerField()
    order = models.ForeignKey(Order,
        on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie,
        on_delete=models.CASCADE)
    def __str__(self):
        return str(self.id) + ' - ' + self.movie.name
