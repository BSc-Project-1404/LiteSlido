from django.shortcuts import render, redirect, get_object_or_404
from .models import Event
from .models import Poll
from .forms import EventForm
from .forms import QuestionForm
from .models import Event
from .forms import PollForm, PollOptionForm
from .models import PollOption
from django.contrib.auth.decorators import login_required
from .models import PollVote 


def event_list(request):
    events = Event.objects.all()
    return render(request, 'events/event_list.html', {'events': events})

def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('event_list')  # Redirect to event list page after saving
    else:
        form = EventForm()
    return render(request, 'events/event_create.html', {'form': form})


def poll_list(request):
    polls = Poll.objects.all()
    return render(request, 'events/poll_list.html', {'polls': polls})

def add_question(request, event_code):
    event = Event.objects.get(code=event_code)
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.event = event
            question.save()
            return redirect('event_list')  # Redirect to event list after saving
    else:
        form = QuestionForm()
    return render(request, 'events/add_question.html', {'form': form, 'event': event})


def add_poll(request, event_code):
    event = Event.objects.get(code=event_code)
    if request.method == 'POST':
        poll_form = PollForm(request.POST)
        num_options = int(request.POST.get('num_options', 0))  # Get the number of options dynamically

        if poll_form.is_valid():
            poll = poll_form.save(commit=False)
            poll.event = event  # Automatically link the poll to the event
            poll.save()

            # Now handle saving poll options (make sure to include the first option)
            for i in range(0, num_options + 1):
                option_text = request.POST.get(f'option_{i}-text')
                if option_text:
                    PollOption.objects.create(poll=poll, text=option_text)

            return redirect('event_detail', event_code=event.code)
    else:
        poll_form = PollForm()
        num_options = 2  # Default to 2 options
        option_forms = [PollOptionForm(prefix=f"option_{i}") for i in range(num_options)]

    return render(request, 'events/add_poll.html', {
        'form': poll_form,
        'option_forms': option_forms,
        'event': event,
        'num_options': num_options,
    })


def event_detail(request, event_code):
    event = get_object_or_404(Event, code=event_code)
    questions = event.questions.all()  # Get all questions for the event
    polls = event.polls.all()  # Get all polls for the event
    return render(request, 'events/event_detail.html', {
        'event': event,
        'questions': questions,
        'polls': polls
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