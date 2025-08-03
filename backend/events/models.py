from django.db import models
import uuid
from django.contrib.auth.models import User


class Event(models.Model):
    code = models.CharField(max_length=10, unique=True, default=uuid.uuid4().hex[:10])
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.code})"


class Question(models.Model):
    event = models.ForeignKey(Event, related_name='questions', on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Q: {self.text[:50]}"


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