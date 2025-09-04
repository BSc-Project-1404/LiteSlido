# core/urls.py
from django.contrib import admin
from django.urls import path, include
from events.views.auth_views import register, custom_login
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', custom_login, name='login'),
    path('accounts/register/', register, name='register'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('accounts/password_change/', auth_views.PasswordChangeView.as_view(success_url='/accounts/password_change/done/'), name='password_change'),
    path('accounts/password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('events/', include('events.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)