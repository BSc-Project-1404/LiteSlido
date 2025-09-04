"""
Question-related views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.contrib import messages
from ..models import Event, Question
from ..forms import QuestionForm, AnonymousQuestionForm
from ..services import (
    add_question_to_event, toggle_question_like, can_user_delete_question,
    delete_question, add_anonymous_question, can_anonymous_view_event
)


@login_required
def add_question(request, event_code):
    """Add a question to an event (authenticated users)"""
    event = get_object_or_404(Event, code=event_code)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            # Use service to add question
            add_question_to_event(
                event=event,
                text=form.cleaned_data['text'],
                author=request.user
            )
            return redirect('event_detail', event_code=event.code)
    else:
        form = QuestionForm()

    return render(request, 'events/add_question.html', {
        'form': form,
        'event': event,
    })


@login_required
def toggle_like(request, question_id):
    """Toggle like status for a question"""
    question = get_object_or_404(Question, id=question_id)
    
    # Use service to toggle like
    toggle_question_like(request.user, question)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def delete_question(request, event_code, question_id):
    """Delete a question (event creator only)"""
    event = get_object_or_404(Event, code=event_code)
    if not can_user_delete_question(request.user, event):
        return HttpResponseForbidden("Only the creator can delete questions.")
    
    question = get_object_or_404(Question, id=question_id, event=event)
    if request.method == 'POST':
        # Use service to delete question
        delete_question(question)
        messages.success(request, "Question deleted.")
        return redirect('event_detail', event_code=event_code)
    # If someone tries GET on this URL, redirect back
    return redirect('event_detail', event_code=event_code)


def anonymous_add_question(request, event_code):
    """View for anonymous users to add questions to events"""
    event = get_object_or_404(Event, code=event_code)
    
    if not can_anonymous_view_event(event):
        return render(request, 'events/event_closed.html', {
            'event': event
        }, status=404)
    
    if request.method == 'POST':
        form = AnonymousQuestionForm(request.POST)
        if form.is_valid():
            # Use service to add anonymous question
            add_anonymous_question(
                event=event,
                author_name=form.cleaned_data['username'],
                text=form.cleaned_data['text']
            )
            return redirect('anonymous_event_detail', event_code=event.code)
    else:
        form = AnonymousQuestionForm()
    
    return render(request, 'events/anonymous_add_question.html', {
        'form': form,
        'event': event,
        'is_anonymous': True,
    })
