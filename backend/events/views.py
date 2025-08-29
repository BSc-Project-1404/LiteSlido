from django.shortcuts import render, redirect, get_object_or_404
from .models import Poll, Question
from .models import Event
from .models import PollOption
from django.contrib.auth.decorators import login_required
from .models import PollVote
from django.http import Http404, HttpResponseForbidden
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponseRedirect
from .services import get_event_list_data, create_event, add_question_to_event, add_poll_to_event, get_event_detail_data, vote_for_poll, get_poll_detail_data, register_user, toggle_question_like, toggle_event_close_status, get_user_profile, edit_user_profile, change_user_password, delete_event_question


@login_required
def event_list(request):
    data = get_event_list_data(request)
    if 'redirect' in data:
        view_name, kwargs = data['redirect']
        return redirect(view_name, **kwargs)
    
    return render(request, 'events/event_list.html', data)


@login_required
def event_create(request):
    data = create_event(request)
    if 'redirect' in data:
        view_name, kwargs = data['redirect']
        return redirect(view_name, **kwargs)
    return render(request, 'events/event_create.html', {'form': data['form']})

@login_required
def add_question(request, event_code):
    data = add_question_to_event(request, event_code)
    if 'redirect' in data:
        view_name, kwargs = data['redirect']
        return redirect(view_name, **kwargs)
    return render(request, 'events/add_question.html', data)

@login_required
def add_poll(request, event_code):
    result = add_poll_to_event(request, event_code)
    if isinstance(result, HttpResponseForbidden):
        return result
    if 'redirect' in result:
        view_name, kwargs = result['redirect']
        return redirect(view_name, **kwargs)
    return render(request, 'events/add_poll.html', result)



@login_required
def event_detail(request, event_code):
    data = get_event_detail_data(request, event_code)
    if 'render' in data:
        view_name, context, status = data['render']
        return render(request, view_name, context, status=status)
    return render(request, 'events/event_detail.html', data)


@login_required
def vote_poll(request, event_code, poll_id):
    data = vote_for_poll(request, event_code, poll_id)
    if 'redirect' in data:
        view_name, kwargs = data['redirect']
        return redirect(view_name, **kwargs)
    return render(request, 'events/vote_poll.html', data)

@login_required
def poll_detail(request, event_code, poll_id):
    data = get_poll_detail_data(request, event_code, poll_id)
    if 'redirect' in data:
        view_name, kwargs = data['redirect']
        return redirect(view_name, **kwargs)
    return render(request, 'events/poll_detail.html', data)


def register(request):
    data = register_user(request)
    if 'redirect' in data:
        view_name, kwargs = data['redirect']
        return redirect(view_name, **kwargs)
    return render(request, 'registration/register.html', {'form': data['form']})

@login_required
def toggle_like(request, question_id):
    return toggle_question_like(request, question_id)

@login_required
def toggle_close(request, event_code):
    result = toggle_event_close_status(request, event_code)
    if isinstance(result, HttpResponseForbidden):
        return result
    view_name, kwargs = result['redirect']
    return redirect(view_name, **kwargs)

@login_required
def profile_view(request):
    data = get_user_profile(request)
    return render(request, 'events/profile.html', data)

@login_required
def profile_edit(request):
    data = edit_user_profile(request)
    if 'redirect' in data:
        view_name, kwargs = data['redirect']
        return redirect(view_name, **kwargs)
    return render(request, 'events/profile_edit.html', {'form': data['form']})

@login_required
def change_password(request):
    data = change_user_password(request)
    if 'redirect' in data:
        view_name, kwargs = data['redirect']
        return redirect(view_name, **kwargs)
    return render(request, 'events/change_password.html', {'form': data['form']})

@login_required
def delete_question(request, event_code, question_id):
    result = delete_event_question(request, event_code, question_id)
    if isinstance(result, HttpResponseForbidden):
        return result
    view_name, kwargs = result['redirect']
    return redirect(view_name, **kwargs)