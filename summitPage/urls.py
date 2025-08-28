
from django.urls import path, include
from . import views


urlpatterns = [
    path('summit/', views.landingEvent, name='summit'),
    path('', views.summit, name='landing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    
    
    path('about/', views.about, name='about'),
    path('agenda/', views.agenda, name='agenda'),
    path('base/', views.base, name='base'),
    path('contact/', views.contact, name='contact'),
    path('features/', views.features, name='features'),
    path('media/', views.media, name='media'),
    path('partners/', views.partners, name='partners'),
    path('register/', views.register, name='register'),
    path('speakers/', views.speakers, name='speakers'),
    path('travel/', views.travel, name='travel'),
    path('home/', views.home, name='home'),
]
