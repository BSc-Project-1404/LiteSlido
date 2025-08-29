# events/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('create/', views.event_create, name='event_create'),
    path('<str:event_code>/', views.event_detail, name='event_detail'),
    path('<str:event_code>/poll/<int:poll_id>/', views.poll_detail, name='poll_detail'), # Poll detail (voting)
    path('<str:event_code>/add_question/', views.add_question, name='add_question'),
    path('<str:event_code>/add_poll/', views.add_poll, name='add_poll'),
    path('question/<int:question_id>/like/', views.toggle_like, name='toggle_like'),
    path('<str:event_code>/toggle_close/', views.toggle_close, name='toggle_close'),
    path('<str:event_code>/question/<int:question_id>/delete/', 
     views.delete_question, 
     name='delete_question'),
    
    # Anonymous user URLs
    path('anonymous/<str:event_code>/', views.anonymous_event_detail, name='anonymous_event_detail'),
    path('anonymous/<str:event_code>/add_question/', views.anonymous_add_question, name='anonymous_add_question'),
]