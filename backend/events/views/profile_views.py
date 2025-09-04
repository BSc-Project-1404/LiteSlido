"""
Profile-related views
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from ..forms import ProfileForm, StyledPasswordChangeForm
from ..services import get_user_profile, update_user_profile


@login_required
def profile_view(request):
    """Display user profile"""
    profile = get_user_profile(request.user)
    return render(request, 'events/profile.html', {'profile': profile})


@login_required
def profile_edit(request):
    """Edit user profile"""
    profile = get_user_profile(request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Use service to update profile
            update_user_profile(
                profile=profile,
                full_name=form.cleaned_data.get('full_name'),
                email=form.cleaned_data.get('email'),
                bio=form.cleaned_data.get('bio'),
                avatar=form.cleaned_data.get('avatar')
            )
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'events/profile_edit.html', {'form': form})


@login_required
def change_password(request):
    """Change user password"""
    if request.method == 'POST':
        form = StyledPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # keep user logged in
            return redirect('profile')
    else:
        form = StyledPasswordChangeForm(user=request.user)
    return render(request, 'events/change_password.html', {'form': form})
