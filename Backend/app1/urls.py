from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='signup'),

    # Shortener
    path('shorts/', views.short_list, name='short_list'),
    path('shorts/create/', views.short_create, name='short_create'),
    path('shorts/<int:pk>/edit/', views.short_edit, name='short_edit'),
    path('shorts/<int:pk>/delete/', views.short_delete, name='short_delete'),
    path('shorts/<int:pk>/stats/', views.short_stats, name='short_stats'),
    path('shorts/<int:pk>/regenerate/', views.short_regenerate, name='short_regenerate'),

    # Redirect route (public)
    path('s/<str:key>/', views.redirect_view, name='short_redirect'),
]