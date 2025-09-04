"""
Question-related business logic services
"""
from django.db.models import Count
from ..models import Event, Question


def get_event_questions(event):
    """Get questions for an event ordered by likes and creation time"""
    return (
        event.questions
             .annotate(num_likes=Count('likes'))
             .order_by('-num_likes', '-created_at')
    )


def add_question_to_event(event, text, author=None, author_name=None):
    """Add a question to an event"""
    return Question.objects.create(
        event=event,
        text=text,
        author=author,
        author_name=author_name
    )


def add_anonymous_question(event, author_name, text):
    """Add an anonymous question to an event"""
    return Question.objects.create(
        event=event,
        author=None,  # Anonymous user
        author_name=author_name,
        text=text
    )


def toggle_question_like(user, question):
    """Toggle like status for a question"""
    if user in question.likes.all():
        question.likes.remove(user)
        return False  # Unliked
    else:
        question.likes.add(user)
        return True  # Liked


def can_user_delete_question(user, event):
    """Check if user can delete questions from event"""
    return user == event.creator


def delete_question(question):
    """Delete a question"""
    question.delete()
