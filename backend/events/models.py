from django.db import models
import uuid
from django.contrib.auth.models import User


def generate_event_code():
    """Return a unique 10-character hexadecimal code."""
    return uuid.uuid4().hex[:10]

class Event(models.Model):
    code = models.CharField(max_length=10, unique=True, default=generate_event_code)
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events')

    def __str__(self):
        return f"{self.title} ({self.code})"



class Question(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='questions')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username} @ {self.event.code}: {self.text[:20]}"


class Poll(models.Model):
    event = models.ForeignKey(Event, related_name='polls', on_delete=models.CASCADE)
    question = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Poll: {self.question}"


class PollOption(models.Model):
    poll = models.ForeignKey(Poll, related_name='options', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)

    def __str__(self):
        return f"Option: {self.text}"

class PollVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poll_option = models.ForeignKey(PollOption, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} voted for {self.poll_option.text}"