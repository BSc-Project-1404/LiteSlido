"""
Event-related business logic services
"""
from django.shortcuts import get_object_or_404
from ..models import Event


def get_user_events(user):
    """Get all events created by a user"""
    return Event.objects.filter(creator=user)


def find_event_by_code(code):
    """Find an event by its code"""
    try:
        return Event.objects.get(code=code)
    except Event.DoesNotExist:
        return None


def create_event(title, creator):
    """Create a new event"""
    return Event.objects.create(
        title=title,
        creator=creator
    )


def can_user_view_event(user, event):
    """Check if user can view event (not closed or user is creator)"""
    return not event.is_closed or user == event.creator


def can_user_close_event(user, event):
    """Check if user can close/open event"""
    return user == event.creator


def toggle_event_close_status(event):
    """Toggle event close status"""
    event.is_closed = not event.is_closed
    event.save()
    return event.is_closed


def can_anonymous_view_event(event):
    """Check if anonymous users can view event (not closed)"""
    return not event.is_closed
