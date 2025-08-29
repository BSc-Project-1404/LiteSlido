# backend/events/admin.py

from django.contrib import admin
from .models import Event, Profile, Question, Poll, PollOption

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'created_at')
    search_fields = ('title', 'code')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('event', 'text', 'author', 'author_name', 'created_at')
    search_fields = ('text', 'author_name')
    list_filter = ('event', 'created_at')

@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ('event', 'question', 'created_at')
    search_fields = ('question',)

@admin.register(PollOption)
class PollOptionAdmin(admin.ModelAdmin):
    list_display = ('poll', 'text')
    search_fields = ('text',)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'bio', 'avatar')
    search_fields = ('full_name',)
