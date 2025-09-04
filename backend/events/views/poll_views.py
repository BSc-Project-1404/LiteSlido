"""
Poll-related views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from ..models import Event, Poll, PollOption
from ..forms import PollForm, PollOptionForm
from ..services import (
    can_user_add_poll, create_poll, get_poll_options,
    has_user_voted_in_poll, vote_in_poll, get_poll_vote_counts
)


@login_required
def add_poll(request, event_code):
    """Add a poll to an event (event creator only)"""
    event = get_object_or_404(Event, code=event_code)

    # Only the creator may add polls
    if not can_user_add_poll(request.user, event):
        return HttpResponseForbidden("You are not allowed to add polls to this event.")

    if request.method == 'POST':
        poll_form = PollForm(request.POST)
        num_options = int(request.POST.get('num_options', 0))

        if poll_form.is_valid():
            # Collect option texts
            options_text = []
            for i in range(0, num_options + 1):
                option_text = request.POST.get(f'option_{i}-text')
                if option_text:
                    options_text.append(option_text)

            # Use service to create poll
            create_poll(
                event=event,
                question=poll_form.cleaned_data['question'],
                options_text=options_text
            )

            return redirect('event_detail', event_code=event.code)
    else:
        poll_form = PollForm()
        num_options = 2
        option_forms = [PollOptionForm(prefix=f"option_{i}") for i in range(num_options)]

    return render(request, 'events/add_poll.html', {
        'form': poll_form,
        'option_forms': option_forms,
        'event': event,
        'num_options': num_options,
    })


@login_required
def vote_poll(request, event_code, poll_id):
    """Vote in a poll"""
    poll = get_object_or_404(Poll, id=poll_id, event__code=event_code)
    options = get_poll_options(poll)
    
    if request.method == 'POST':
        selected_option_id = request.POST.get('poll_option')
        selected_option = get_object_or_404(PollOption, id=selected_option_id)

        # Check if the user has already voted for this poll
        if not has_user_voted_in_poll(request.user, poll):
            vote_in_poll(request.user, selected_option)
            return redirect('event_detail', event_code=event_code)

    return render(request, 'events/vote_poll.html', {
        'poll': poll,
        'options': options,
        'event_code': event_code,
    })


@login_required
def poll_detail(request, event_code, poll_id):
    """Display poll results"""
    event = get_object_or_404(Event, code=event_code)
    poll = get_object_or_404(Poll, id=poll_id, event=event)
    user_has_voted = has_user_voted_in_poll(request.user, poll)

    if request.method == 'POST' and not user_has_voted:
        selected_option_id = request.POST.get('poll_option')
        selected_option = get_object_or_404(PollOption, id=selected_option_id, poll=poll)
        vote_in_poll(request.user, selected_option)
        return redirect('poll_detail', event_code=event_code, poll_id=poll_id)

    # Use service to get vote counts
    option_votes_list = get_poll_vote_counts(poll)

    return render(request, 'events/poll_detail.html', {
        'event': event,
        'poll': poll,
        'user_has_voted': user_has_voted,
        'option_votes_list': option_votes_list,
    })
