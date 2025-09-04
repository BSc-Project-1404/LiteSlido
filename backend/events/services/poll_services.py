"""
Poll-related business logic services
"""
from ..models import Poll, PollOption, PollVote


def get_event_polls(event):
    """Get polls for an event"""
    return event.polls.all()


def create_poll(event, question, options_text):
    """Create a poll with options"""
    poll = Poll.objects.create(
        event=event,
        question=question
    )
    
    for option_text in options_text:
        if option_text.strip():
            PollOption.objects.create(poll=poll, text=option_text.strip())
    
    return poll


def can_user_add_poll(user, event):
    """Check if user can add polls to event"""
    return user == event.creator


def get_poll_options(poll):
    """Get options for a poll"""
    return poll.options.all()


def has_user_voted_in_poll(user, poll):
    """Check if user has already voted in poll"""
    return PollVote.objects.filter(user=user, poll_option__poll=poll).exists()


def vote_in_poll(user, poll_option):
    """Record a vote for a poll option"""
    return PollVote.objects.create(user=user, poll_option=poll_option)


def get_poll_vote_counts(poll):
    """Get vote counts for each option in a poll"""
    options = poll.options.all()
    option_votes_list = []
    for option in options:
        count = PollVote.objects.filter(poll_option=option).count()
        option_votes_list.append((option, count))
    return option_votes_list
