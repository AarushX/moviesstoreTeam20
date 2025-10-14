from django.db import models
from django.contrib.auth.models import User

class Petition(models.Model):
    id = models.AutoField(primary_key=True)
    movie_name = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='petitions_created')
    created_at = models.DateTimeField(auto_now_add=True)
    voters = models.ManyToManyField(User, related_name='petitions_voted', blank=True)
    
    def vote_count(self):
        return self.voters.count()
    
    def __str__(self):
        return str(self.id) + ' - ' + self.movie_name
    
    class Meta:
        ordering = ['-created_at']