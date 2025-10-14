from django import forms
from .models import Petition

class PetitionForm(forms.ModelForm):
    class Meta:
        model = Petition
        fields = ['movie_name']
        widgets = {
            'movie_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter movie name'
            })
        }
        labels = {
            'movie_name': 'Movie Name'
        }