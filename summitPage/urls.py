
from django.urls import path, include
from . import views
from .views import SummitLoginView, SummitLogoutView

from rest_framework.routers import DefaultRouter
from .views import *
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

# router = DefaultRouter()
# router.register(r'events', EventViewSet)
# router.register(r'tracks', TrackViewSet)
# router.register(r'sessions', SessionViewSet)
# router.register(r'speakers', SpeakerViewSet)
# router.register(r'exhibitors', ExhibitorViewSet)
# router.register(r'sponsors', SponsorViewSet)
# router.register(r'registrations', RegistrationViewSet)
# router.register(r'tickets', TicketViewSet)
# router.register(r'orders', OrderViewSet)
# router.register(r'payments', PaymentViewSet)
# router.register(r'connections', ConnectionViewSet)
# router.register(r'chat', ChatMessageViewSet)
# router.register(r'polls', PollViewSet)
# router.register(r'poll-options', PollOptionViewSet)
# router.register(r'poll-votes', PollVoteViewSet)
# router.register(r'qna', QnAViewSet)
# router.register(r'feedback', FeedbackViewSet)
# router.register(r'notifications', NotificationViewSet)


urlpatterns = [
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("mailme/", views.mailme_view, name="mailme"),
    path("dashboard/data/", views.dashboard_data, name="dashboard_data"),
    path("index/", views.index, name="index"),
    path("delete/<int:pk>/", views.delete_registrant, name="delete_registrant"),
    path("privacy/", views.privacy, name="privacy"),
    path("404/", views.not_found, name="not_found"),
    path("speakers/", views.speakers, name="speakers"),
    path("media/", views.media, name="media"),
    # path("register/", views.register, name="register"),

    
    path("login/", SummitLoginView.as_view(), name="custom_login"),
    path("logout/", SummitLogoutView.as_view(), name="logout"),
    path("export/print/", views.print_registrants, name="export_print"),
    path("unsubscribe/<uuid:token>/", views.unsubscribe_view, name="unsubscribe"),
    path('dashboard/stats/', views.dashboard_stats, name='dashboard_stats'),
    path("export/excel/", views.export_registrants_excel, name="export_excel"),
    path('', views.home, name='home'),



    path('badge/<int:registrant_id>/', views.generate_badge, name='generate_badge'),
    
    # path("api/", include(router.urls)),
]