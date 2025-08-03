# events/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('create/', views.event_create, name='event_create'),
    path('<str:event_code>/', views.event_detail, name='event_detail'),
    path('<str:event_code>/poll/<int:poll_id>/', views.poll_detail, name='poll_detail'), # Poll detail (voting)
    path('<str:event_code>/add_question/', views.add_question, name='add_question'),
    path('<str:event_code>/add_poll/', views.add_poll, name='add_poll'),
    path('question/<int:question_id>/like/', views.toggle_like, name='toggle_like'),
    path('<str:event_code>/toggle_close/', views.toggle_close, name='toggle_close'),
]