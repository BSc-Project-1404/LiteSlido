"""
Event-related views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from ..models import Event
from ..forms import EventForm
from ..services import (
    get_user_events, find_event_by_code, create_event,
    can_user_view_event, get_event_questions, get_event_polls,
    can_anonymous_view_event
)


@login_required
def event_list(request):
    """Display list of user's events and handle joining by code"""
    # Show only events created by this user
    my_events = get_user_events(request.user)
    
    # Handle join by code
    join_error = None
    if request.method == 'POST':
        code = request.POST.get('event_code', '').strip()
        event = find_event_by_code(code)
        if event:
            return redirect('event_detail', event_code=event.code)
        else:
            join_error = "Invalid event code."

    return render(request, 'events/event_list.html', {
        'my_events': my_events,
        'join_error': join_error,
    })


@login_required
def event_create(request):
    """Create a new event"""
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            # Use service to create event
            event = create_event(
                title=form.cleaned_data['title'],
                creator=request.user
            )
            return redirect('event_list')
    else:
        form = EventForm()
    return render(request, 'events/event_create.html', {'form': form})


@login_required
def event_detail(request, event_code):
    """Display event details for authenticated users"""
    event = get_object_or_404(Event, code=event_code)

    # If closed and not creator, show custom closed page with 404 status
    if not can_user_view_event(request.user, event):
        return render(request, 'events/event_closed.html', {
            'event': event
        }, status=404)

    # Use services to get data
    questions = get_event_questions(event)
    polls = get_event_polls(event)

    return render(request, 'events/event_detail.html', {
        'event': event,
        'questions': questions,
        'polls': polls,
    })


@login_required
def toggle_close(request, event_code):
    """Toggle event close/open status"""
    event = get_object_or_404(Event, code=event_code)
    if not can_user_close_event(request.user, event):
        return HttpResponseForbidden("Only the creator can close or open this event.")
    
    # Use service to toggle close status
    from ..services import toggle_event_close_status
    toggle_event_close_status(event)
    return redirect('event_detail', event_code=event.code)


def anonymous_event_detail(request, event_code):
    """View for anonymous users to view events and ask questions"""
    event = get_object_or_404(Event, code=event_code)
    
    if not can_anonymous_view_event(event):
        return render(request, 'events/event_closed.html', {
            'event': event
        }, status=404)
    
    # Use services to get data
    questions = get_event_questions(event)
    polls = get_event_polls(event)
    
    return render(request, 'events/anonymous_event_detail.html', {
        'event': event,
        'questions': questions,
        'polls': polls,
        'is_anonymous': True,
    })
