
from django.urls import path, include
from . import views


urlpatterns = [
    path('summit/', views.landingEvent, name='summit'),
    path('alt/', views.summit, name='landing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),

    path("unsubscribe/<uuid:token>/", views.unsubscribe_view, name="unsubscribe"),
    path('bulk-email/', views.bulk_email_view, name='bulk_email'),
    path('dashboard/stats/', views.dashboard_stats, name='dashboard_stats'),
    path('export/csv/', views.export_csv, name='export_csv'),
    path('export/excel/', views.export_excel, name='export_excel'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
    path('', views.home, name='home'),
]

