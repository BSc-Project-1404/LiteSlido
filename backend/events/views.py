from django.shortcuts import render, redirect, get_object_or_404
from .models import Event
from .models import Poll, Question
from .forms import EventForm
from .forms import QuestionForm
from .models import Event
from .forms import PollForm, PollOptionForm
from .models import PollOption
from django.contrib.auth.decorators import login_required
from .models import PollVote 
from django.contrib.auth.forms import UserCreationForm
from django.http import Http404, HttpResponseForbidden
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import ProfileForm
from django.http import HttpResponseRedirect
from django.contrib import messages


@login_required
def event_list(request):
    # Show only events created by this user
    my_events = Event.objects.filter(creator=request.user)
    
    # Handle join by code
    join_error = None
    if request.method == 'POST':
        code = request.POST.get('event_code', '').strip()
        try:
            event = get_object_or_404(Event, code=code)
            return redirect('event_detail', event_code=event.code)
        except:
            join_error = "Invalid event code."

    return render(request, 'events/event_list.html', {
        'my_events': my_events,
        'join_error': join_error,
    })


@login_required
def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            # Don’t save to DB yet—attach creator first
            event = form.save(commit=False)
            event.creator = request.user
            event.save()
            return redirect('event_list')
    else:
        form = EventForm()
    return render(request, 'events/event_create.html', {'form': form})

@login_required
def add_question(request, event_code):
    event = get_object_or_404(Event, code=event_code)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.event = event
            question.author = request.user      # ← Set the author here
            question.save()
            return redirect('event_detail', event_code=event.code)
    else:
        form = QuestionForm()

    return render(request, 'events/add_question.html', {
        'form': form,
        'event': event,
    })

def add_poll(request, event_code):
    event = get_object_or_404(Event, code=event_code)

    # Only the creator may add polls
    if request.user != event.creator:
        return HttpResponseForbidden("You are not allowed to add polls to this event.")

    if request.method == 'POST':
        poll_form = PollForm(request.POST)
        num_options = int(request.POST.get('num_options', 0))

        if poll_form.is_valid():
            poll = poll_form.save(commit=False)
            poll.event = event
            poll.save()

            for i in range(0, num_options + 1):
                option_text = request.POST.get(f'option_{i}-text')
                if option_text:
                    PollOption.objects.create(poll=poll, text=option_text)

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


from django.db.models import Count

@login_required
def event_detail(request, event_code):
    event = get_object_or_404(Event, code=event_code)

    # If closed and not creator, show custom closed page with 404 status
    if event.is_closed and request.user != event.creator:
        return render(request, 'events/event_closed.html', {
            'event': event
        }, status=404)

    # Annotate questions by like count, descending
    questions = (
        event.questions
             .annotate(num_likes=Count('likes'))
             .order_by('-num_likes', '-created_at')
    )
    polls = event.polls.all()

    return render(request, 'events/event_detail.html', {
        'event': event,
        'questions': questions,
        'polls': polls,
    })


@login_required
def vote_poll(request, event_code, poll_id):
    poll = get_object_or_404(Poll, id=poll_id, event__code=event_code)
    options = poll.options.all()
    
    if request.method == 'POST':
        selected_option_id = request.POST.get('poll_option')
        selected_option = get_object_or_404(PollOption, id=selected_option_id)

        # Check if the user has already voted for this poll
        if not PollVote.objects.filter(user=request.user, poll_option__poll=poll).exists():
            PollVote.objects.create(user=request.user, poll_option=selected_option)
            return redirect('event_detail', event_code=event_code)

    return render(request, 'events/vote_poll.html', {
        'poll': poll,
        'options': options,
        'event_code': event_code,
    })

@login_required
def poll_detail(request, event_code, poll_id):
    event = get_object_or_404(Event, code=event_code)
    poll = get_object_or_404(Poll, id=poll_id, event=event)
    options = poll.options.all()
    user_has_voted = PollVote.objects.filter(user=request.user, poll_option__poll=poll).exists()

    if request.method == 'POST' and not user_has_voted:
        selected_option_id = request.POST.get('poll_option')
        selected_option = get_object_or_404(PollOption, id=selected_option_id, poll=poll)
        PollVote.objects.create(user=request.user, poll_option=selected_option)
        return redirect('poll_detail', event_code=event_code, poll_id=poll_id)

    # Build list of (option, vote_count)
    option_votes_list = []
    for option in options:
        count = PollVote.objects.filter(poll_option=option).count()
        option_votes_list.append((option, count))

    return render(request, 'events/poll_detail.html', {
        'event': event,
        'poll': poll,
        'user_has_voted': user_has_voted,
        'option_votes_list': option_votes_list,
    })



def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Save user
            user = form.save()
            # Authenticate and log in the new user
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            if user:
                login(request, user)
                return redirect('event_list')
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})

@login_required
def toggle_like(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    user = request.user

    if user in question.likes.all():
        question.likes.remove(user)
    else:
        question.likes.add(user)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def toggle_close(request, event_code):
    event = get_object_or_404(Event, code=event_code)
    if request.user != event.creator:
        return HttpResponseForbidden("Only the creator can close or open this event.")
    event.is_closed = not event.is_closed
    event.save()
    return redirect('event_detail', event_code=event.code)

@login_required
def profile_view(request):
    profile = request.user.profile
    return render(request, 'events/profile.html', {'profile': profile})

@login_required
def profile_edit(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'events/profile_edit.html', {'form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # keep user logged in
            return redirect('profile')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'events/change_password.html', {'form': form})

@login_required
def delete_question(request, event_code, question_id):
    event = get_object_or_404(Event, code=event_code)
    if request.user != event.creator:
        return HttpResponseForbidden("Only the creator can delete questions.")
    question = get_object_or_404(Question, id=question_id, event=event)
    if request.method == 'POST':
        question.delete()
        messages.success(request, "Question deleted.")
        return redirect('event_detail', event_code=event_code)
    # If someone tries GET on this URL, redirect back
    return redirect('event_detail', event_code=event_code)