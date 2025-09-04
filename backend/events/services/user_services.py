"""
User-related business logic services
"""
from django.contrib.auth.models import User


def create_user(username, email, password):
    """Create a new user"""
    return User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
