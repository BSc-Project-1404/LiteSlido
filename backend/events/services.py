from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseForbidden, HttpResponseRedirect
from .models import Event, Question, Poll, PollOption, PollVote
from .forms import EventForm, QuestionForm, PollForm, PollOptionForm, ProfileForm, AnonymousQuestionForm, StyledUserCreationForm, StyledPasswordChangeForm
from django.db.models import Count
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib import messages


def get_event_list_data(request):
    my_events = Event.objects.filter(creator=request.user)
    join_error = None
    
    if request.method == 'POST':
        code = request.POST.get('event_code', '').strip()
        try:
            event = get_object_or_404(Event, code=code)
            return {'redirect': ('event_detail', {'event_code': event.code})}
        except:
            join_error = "Invalid event code."

    return {
        'my_events': my_events,
        'join_error': join_error,
    }


def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.creator = request.user
            event.save()
            return {'redirect': ('event_list', {})}
    else:
        form = EventForm()
    return {'form': form}


def add_question_to_event(request, event_code):
    event = get_object_or_404(Event, code=event_code)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.event = event
            question.author = request.user  # Logged-in user
            question.save()
            return {'redirect': ('event_detail', {'event_code': event.code})}
    else:
        form = QuestionForm()

    return {
        'form': form,
        'event': event,
    }


def add_poll_to_event(request, event_code):
    event = get_object_or_404(Event, code=event_code)

    if request.user != event.creator:
        return HttpResponseForbidden("You are not allowed to add polls to this event.")

    if request.method == 'POST':
        poll_form = PollForm(request.POST)
        num_options = int(request.POST.get('num_options', 0))
        option_forms = [] # Initialize here to ensure it's always defined

        if poll_form.is_valid():
            poll = poll_form.save(commit=False)
            poll.event = event
            poll.save()

            for i in range(0, num_options + 1):
                option_text = request.POST.get(f'option_{i}-text')
                if option_text:
                    PollOption.objects.create(poll=poll, text=option_text)

            return {'redirect': ('event_detail', {'event_code': event.code})}
    else:
        poll_form = PollForm()
        num_options = 2
        option_forms = [PollOptionForm(prefix=f"option_{i}") for i in range(num_options)]

    return {
        'form': poll_form,
        'option_forms': option_forms,
        'event': event,
        'num_options': num_options,
    }


def get_event_detail_data(request, event_code):
    event = get_object_or_404(Event, code=event_code)

    if event.is_closed and request.user != event.creator:
        return {
            'render': ('events/event_closed.html', {
                'event': event
            }, 404)
        }

    questions = (
        event.questions
             .annotate(num_likes=Count('likes'))
             .order_by('-num_likes', '-created_at')
    )
    polls = event.polls.all()

    return {
        'event': event,
        'questions': questions,
        'polls': polls,
    }


def vote_for_poll(request, event_code, poll_id):
    poll = get_object_or_404(Poll, id=poll_id, event__code=event_code)
    options = poll.options.all()
    
    if request.method == 'POST':
        selected_option_id = request.POST.get('poll_option')
        selected_option = get_object_or_404(PollOption, id=selected_option_id)

        if not PollVote.objects.filter(user=request.user, poll_option__poll=poll).exists():
            PollVote.objects.create(user=request.user, poll_option=selected_option)
            return {'redirect': ('event_detail', {'event_code': event_code})}

    return {
        'poll': poll,
        'options': options,
        'event_code': event_code,
    }


def get_poll_detail_data(request, event_code, poll_id):
    event = get_object_or_404(Event, code=event_code)
    poll = get_object_or_404(Poll, id=poll_id, event=event)
    options = poll.options.all()
    user_has_voted = PollVote.objects.filter(user=request.user, poll_option__poll=poll).exists()

    if request.method == 'POST' and not user_has_voted:
        selected_option_id = request.POST.get('poll_option')
        selected_option = get_object_or_404(PollOption, id=selected_option_id, poll=poll)
        PollVote.objects.create(user=request.user, poll_option=selected_option)
        return {'redirect': ('poll_detail', {'event_code': event_code, 'poll_id': poll_id})}

    option_votes_list = []
    for option in options:
        count = PollVote.objects.filter(poll_option=option).count()
        option_votes_list.append((option, count))

    return {
        'event': event,
        'poll': poll,
        'user_has_voted': user_has_voted,
        'option_votes_list': option_votes_list,
    }


def register_user(request):
    if request.method == 'POST':
        form = StyledUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            if user:
                login(request, user)
                return {'redirect': ('event_list', {})}
    else:
        form = StyledUserCreationForm()

    return {'form': form}


def toggle_question_like(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    user = request.user

    if user in question.likes.all():
        question.likes.remove(user)
    else:
        question.likes.add(user)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def toggle_event_close_status(request, event_code):
    event = get_object_or_404(Event, code=event_code)
    if request.user != event.creator:
        return HttpResponseForbidden("Only the creator can close or open this event.")
    event.is_closed = not event.is_closed
    event.save()
    return {'redirect': ('event_detail', {'event_code': event.code})}


def get_user_profile(request):
    profile = request.user.profile
    return {'profile': profile}


def edit_user_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return {'redirect': ('profile', {})}
    else:
        form = ProfileForm(instance=profile)
    return {'form': form}


def change_user_password(request):
    if request.method == 'POST':
        form = StyledPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return {'redirect': ('profile', {})}
    else:
        form = StyledPasswordChangeForm(user=request.user)
    return {'form': form}


def delete_event_question(request, event_code, question_id):
    event = get_object_or_404(Event, code=event_code)
    if request.user != event.creator:
        return HttpResponseForbidden("Only the creator can delete questions.")
    question = get_object_or_404(Question, id=question_id, event=event)
    if request.method == 'POST':
        question.delete()
        messages.success(request, "Question deleted.")
        return {'redirect': ('event_detail', {'event_code': event_code})}
    return {'redirect': ('event_detail', {'event_code': event_code})}


def get_anonymous_event_data(request, event_code):
    """Service for anonymous users to view events and ask questions"""
    event = get_object_or_404(Event, code=event_code)
    
    if event.is_closed:
        return {
            'render': ('events/event_closed.html', {
                'event': event
            }, 404)
        }
    
    questions = (
        event.questions
             .annotate(num_likes=Count('likes'))
             .order_by('-num_likes', '-created_at')
    )
    polls = event.polls.all()
    
    return {
        'event': event,
        'questions': questions,
        'polls': polls,
        'is_anonymous': True,
    }


def add_anonymous_question_to_event(request, event_code):
    """Service for anonymous users to add questions to events"""
    event = get_object_or_404(Event, code=event_code)
    
    if event.is_closed:
        return {
            'render': ('events/event_closed.html', {
                'event': event
            }, 404)
        }
    
    if request.method == 'POST':
        form = AnonymousQuestionForm(request.POST)
        if form.is_valid():
            question = Question.objects.create(
                event=event,
                author=None,  # Anonymous user
                author_name=form.cleaned_data['username'],
                text=form.cleaned_data['text']
            )
            return {'redirect': ('anonymous_event_detail', {'event_code': event.code})}
    else:
        form = AnonymousQuestionForm()
    
    return {
        'form': form,
        'event': event,
        'is_anonymous': True,
    }


