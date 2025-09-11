
from django.urls import path, include
from . import views
from .views import SummitLoginView, SummitLogoutView


urlpatterns = [
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("dashboard/data/", views.dashboard_data, name="dashboard_data"),
    
    path("login/", SummitLoginView.as_view(), name="custom_login"),
    path("logout/", SummitLogoutView.as_view(), name="logout"),
    path("export/print/", views.print_registrants, name="export_print"),

    path("unsubscribe/<uuid:token>/", views.unsubscribe_view, name="unsubscribe"),
    path('bulk-email/', views.bulk_email_view, name='bulk_email'),
    path('dashboard/stats/', views.dashboard_stats, name='dashboard_stats'),
    path("export/csv/", views.export_registrants_csv, name="export_csv"),
    path("export/excel/", views.export_registrants_excel, name="export_excel"),
    path("export/pdf/", views.export_registrants_pdf, name="export_pdf"),
    
    # path('', views.agenda, name='agenda'),
    path('', views.home, name='home'),
]