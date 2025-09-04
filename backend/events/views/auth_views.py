"""
Authentication-related views
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from ..forms import StyledAuthenticationForm, StyledUserCreationForm
from ..services import create_user


def custom_login(request):
    """Custom login view that provides proper form context"""
    if request.user.is_authenticated:
        return redirect('event_list')
    
    if request.method == 'POST':
        form = StyledAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('event_list')
    else:
        form = StyledAuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})


def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = StyledUserCreationForm(request.POST)
        if form.is_valid():
            # Use service to create user
            user = create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data.get('email', ''),
                password=form.cleaned_data['password1']
            )
            # Authenticate and log in the new user
            user = authenticate(username=user.username, password=form.cleaned_data['password1'])
            if user:
                login(request, user)
                return redirect('event_list')
    else:
        form = StyledUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})
