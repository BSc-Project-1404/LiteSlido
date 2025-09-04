# events/urls.py
from django.urls import path
from .views import (
    event_views, question_views, poll_views, 
    auth_views, profile_views
)

urlpatterns = [
    # Event views
    path('', event_views.event_list, name='event_list'),
    path('create/', event_views.event_create, name='event_create'),
    path('<str:event_code>/', event_views.event_detail, name='event_detail'),
    path('<str:event_code>/toggle_close/', event_views.toggle_close, name='toggle_close'),
    
    # Question views
    path('<str:event_code>/add_question/', question_views.add_question, name='add_question'),
    path('question/<int:question_id>/like/', question_views.toggle_like, name='toggle_like'),
    path('<str:event_code>/question/<int:question_id>/delete/', 
         question_views.delete_question, name='delete_question'),
    
    # Poll views
    path('<str:event_code>/add_poll/', poll_views.add_poll, name='add_poll'),
    path('<str:event_code>/poll/<int:poll_id>/', poll_views.poll_detail, name='poll_detail'),
    path('<str:event_code>/poll/<int:poll_id>/vote/', poll_views.vote_poll, name='vote_poll'),
    
    # Profile views
    path('profile/', profile_views.profile_view, name='profile'),
    path('profile/edit/', profile_views.profile_edit, name='profile_edit'),
    path('profile/change-password/', profile_views.change_password, name='change_password'),
    
    # Anonymous user URLs
    path('anonymous/<str:event_code>/', event_views.anonymous_event_detail, name='anonymous_event_detail'),
    path('anonymous/<str:event_code>/add_question/', question_views.anonymous_add_question, name='anonymous_add_question'),
]