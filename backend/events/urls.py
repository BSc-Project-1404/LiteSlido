# events/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('create/', views.event_create, name='event_create'),
    path('polls/', views.poll_list, name='poll_list'),
    path('<str:event_code>/', views.event_detail, name='event_detail'),
    path('<str:event_code>/add_question/', views.add_question, name='add_question'),  # Add question view
    path('<str:event_code>/add_poll/', views.add_poll, name='add_poll'),
    path('<str:event_code>/poll/<int:poll_id>/vote/', views.vote_poll, name='vote_poll'),
]