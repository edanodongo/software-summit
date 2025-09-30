
from django.urls import path, include
from . import views
from .views import SummitLoginView, SummitLogoutView

urlpatterns = [
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("dashboard/data/", views.dashboard_data, name="dashboard_data"),
    path("index/", views.index, name="index"),
    path("delete/<int:pk>/", views.delete_registrant, name="delete_registrant"),
    path("privacy/", views.privacy, name="privacy"),
    path("404/", views.not_found, name="not_found"),

    
    path("login/", SummitLoginView.as_view(), name="custom_login"),
    path("logout/", SummitLogoutView.as_view(), name="logout"),
    path("export/print/", views.print_registrants, name="export_print"),
    path("unsubscribe/<uuid:token>/", views.unsubscribe_view, name="unsubscribe"),
    path('dashboard/stats/', views.dashboard_stats, name='dashboard_stats'),
    path("export/excel/", views.export_registrants_excel, name="export_excel"),
    path('', views.home, name='home'),
]