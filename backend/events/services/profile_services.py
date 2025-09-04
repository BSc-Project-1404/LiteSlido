"""
Profile-related business logic services
"""
from ..models import Profile


def get_user_profile(user):
    """Get user profile"""
    return user.profile


def update_user_profile(profile, full_name=None, email=None, bio=None, avatar=None):
    """Update user profile"""
    if full_name is not None:
        profile.full_name = full_name
    if email is not None:
        profile.email = email
    if bio is not None:
        profile.bio = bio
    if avatar is not None:
        profile.avatar = avatar
    profile.save()
    return profile
