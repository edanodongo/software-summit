from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.routers import DefaultRouter

from . import views
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

    path('sendMail/', views.sendMail, name='sendMail'),

    path('badge/<int:registrant_id>/', views.generate_badge, name='generate_badge'),

    # Registration API
    path('reg-service/registrations/', views.get_registrants, name='get_registrants'),
    # path("api/", include(router.urls)),



    path("register", views.reg, name="register"),
    path('calendar/add/', views.add_to_calendar, name='add_to_calendar'),
    path('resend-email/<int:registrant_id>/', views.resend_confirmation_email, name='resend_confirmation_email'),
    path('dashboard/data/', views.dashboard_data, name='dashboard_data'),

    #SHEDULE 

    path("schedule/home", views.dashboard_home, name="dashboard_home"),       
    # Day CRUD
    path("day/add/", views.add_day, name="add_day"),
    path("day/<int:pk>/edit/", views.edit_day, name="edit_day"),
    path("day/<int:pk>/delete/", views.delete_day, name="delete_day"),
    # Timeslot CRUD
    path("timeslot/add/<int:day_id>/", views.add_timeslot, name="add_timeslot"),
    # Session CRUD (with panelists)
    path("session/add/<int:timeslot_id>/", views.add_session, name="add_session"),
    path("session/<int:pk>/edit/", views.edit_session, name="edit_session"),
    path("session/<int:pk>/delete/", views.delete_session, name="delete_session"),


    #SPEAKERS

    path("dashboard/speakers/", views.speaker_dashboard, name="speaker_dashboard"),
    path("speakers/add/", views.speaker_create, name="speaker_create"),
    path("dashboard/speakers/<uuid:pk>/edit/", views.update_speaker, name="update_speaker"),
    path("dashboard/speakers/<uuid:pk>/delete/", views.delete_speaker, name="delete_speaker"),

    #PARTNERS

    path("partners/dashboard/", views.partner_dashboard, name="partner_dashboard"),
    path("partners/save/", views.save_partner, name="save_partner"),
    path("partners/delete/<uuid:partner_id>/", views.delete_partner, name="delete_partner"),

    #GALLERY

    path('gallery-dashboard/', views.gallery_dashboard, name='gallery_dashboard'),
    path('gallery/edit/<int:pk>/', views.gallery_edit, name='gallery_edit'),
    path('gallery/delete/<int:pk>/', views.gallery_delete, name='gallery_delete'),
]
