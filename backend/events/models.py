from django.db import models
import uuid
from django.contrib.auth.models import User
from PIL import Image


def generate_event_code():
    """Return a unique 10-character hexadecimal code."""
    return uuid.uuid4().hex[:10]

class Event(models.Model):
    code = models.CharField(max_length=10, unique=True, default=generate_event_code)
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events')
    is_closed = models.BooleanField(default=False)   # ← New field

    def __str__(self):
        return f"{self.title} ({self.code})"
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(max_length=254, blank=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Resize avatar to 300x300 max
        if self.avatar:
            img = Image.open(self.avatar.path)
            img.thumbnail((300, 300))
            img.save(self.avatar.path)



class Question(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='questions')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions', null=True, blank=True)
    author_name = models.CharField(max_length=150, blank=True, null=True)  # For anonymous questions
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_questions', blank=True)

    def like_count(self):
        return self.likes.count()

    def get_author_display(self):
        """Return the author name to display"""
        if self.author:
            return self.author.username
        return self.author_name if self.author_name else "Anonymous"

    def is_anonymous(self):
        """Check if this is an anonymous question"""
        return self.author is None

    def __str__(self):
        author_display = self.get_author_display()
        return f"{author_display} @ {self.event.code}: {self.text[:20]}"


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