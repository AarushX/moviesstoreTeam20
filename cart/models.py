from django.db import models
from django.contrib.auth.models import User
from movies.models import Movie

class Order(models.Model):
    id = models.AutoField(primary_key=True)
    total = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User,
        on_delete=models.CASCADE)
    region = models.CharField(max_length=100, blank=True, null=True, help_text="Geographic region of purchase")
    city = models.CharField(max_length=100, blank=True, null=True, help_text="City of purchase")
    state = models.CharField(max_length=100, blank=True, null=True, help_text="State/province of purchase")
    country = models.CharField(max_length=100, default='USA', help_text="Country of purchase")
    def __str__(self):
        return str(self.id) + ' - ' + self.user.username

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
