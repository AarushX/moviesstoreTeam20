
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Petition
from .forms import PetitionForm

def index(request):
    template_data = {}
    template_data['title'] = 'Petitions'
    template_data['petitions'] = Petition.objects.all()
    template_data['form'] = PetitionForm()
    return render(request, 'petitions/index.html', {'template_data': template_data})

@login_required
def create(request):
    if request.method == 'POST':
        form = PetitionForm(request.POST)
        if form.is_valid():
            petition = form.save(commit=False)
            petition.created_by = request.user
            petition.save()
            return redirect('petitions.index')
    return redirect('petitions.index')

@login_required
def vote(request, id):
    petition = get_object_or_404(Petition, id=id)
    
    if request.user in petition.voters.all():
        # User already voted, remove their vote
        petition.voters.remove(request.user)
    else:
        # User hasn't voted, add their vote
        petition.voters.add(request.user)
    
    return redirect('petitions.index')
