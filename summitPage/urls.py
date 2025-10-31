from django.urls import path

from . import views
from .views import *

urlpatterns = [
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("dashboard/student", views.dashboard_student_view, name="student"),
    path("mailme/", views.mailme_view, name="mailme"),
    # path("protocol/", views.protocol, name="protocol"),
    path("register-org/", views.special_registration, name="special_registration"),
    path("register/", views.reg, name="register"),
    path('registrant/<int:registrant_id>/edit/', views.edit_registrant, name='edit_registrant'),
    path('registrant/<int:registrant_id>/edit/modal/', views.edit_registrant_modal, name='edit_registrant_modal'),
    path("edit-exhibitor/<uuid:exhibitor_id>/", views.edit_exhibitor_modal, name="edit_exhibitor_modal"),

    # category setup
    path("categories/", views.guest_category, name="categories"),
    path("categories/add/", views.categories_create, name="categories_create"),
    path('categories/saveCategory/', views.save_category, name='saveCategory'),
    path("categories/<int:pk>/edit", views.update_category, name="update_category"),
    path("categories/<int:pk>/delete/", views.delete_category, name="delete_category"),
    path('categories/editCategory/', views.edit_category, name='editCategory'),

    path("index/", views.index, name="index"),
    path("privacy/", views.privacy, name="privacy"),
    path("404/", views.not_found, name="not_found"),
    path("speakers/", views.speakers, name="speakers"),
    path("media/", views.media, name="media"),
    path("places/", views.places, name="places"),

    path("login/", SummitLoginView.as_view(), name="custom_login"),
    path("logout/", SummitLogoutView.as_view(), name="logout"),
    path("export/print/", views.print_registrants, name="export_print"),
    path("unsubscribe/<uuid:token>/", views.unsubscribe_view, name="unsubscribe"),
    path('dashboard/stats/', views.dashboard_stats, name='dashboard_stats'),
    path("export/excel/", views.export_registrants_excel, name="export_excel"),
    path('', views.home, name='home'),

    path('sendMail/', views.sendMail, name='sendMail'),

    path('badge/<int:registrant_id>/', views.generate_badge, name='generate_badge'),

    path('badge/<uuid:exhibitor_id>/', views.generate_exhibitor_badge, name='generate_exhibitor_badge'),
    path('resend-email/<uuid:exhibitor_id>', views.resend_exhibitor_confirmation_email,
         name='resend_exhibitor_confirmation_email'),

    # Registration API
    path('reg-service/registrations/', views.get_registrants, name='get_registrants'),
    # path("api/", include(router.urls)),
    path("dashboard-main/", views.main_dashboard_view, name="main_dashboard_view"),

    path("register", views.reg, name="register"),
    path('calendar/add/', views.add_to_calendar, name='add_to_calendar'),
    path('resend-email/<int:registrant_id>/', views.resend_confirmation_email, name='resend_confirmation_email'),
    path('approve-student/<int:registrant_id>/', views.approve_student, name='approve_student'),
    path('delete/<int:pk>/', views.delete_registrant, name='delete_registrant'),
    path('dashboard/data/', views.dashboard_data, name='dashboard_data'),

    # SHEDULE

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

    # SPEAKERS

    path("dashboard/speakers/", views.speaker_dashboard, name="speaker_dashboard"),
    path("speakers/add/", views.speaker_create, name="speaker_create"),
    path("dashboard/speakers/<uuid:pk>/edit/", views.update_speaker, name="update_speaker"),
    path("dashboard/speakers/<uuid:pk>/delete/", views.delete_speaker, name="delete_speaker"),

    # PARTNERS

    path("partners/dashboard/", views.partner_dashboard, name="partner_dashboard"),
    path("partners/save/", views.save_partner, name="save_partner"),
    path("partners/delete/<uuid:partner_id>/", views.delete_partner, name="delete_partner"),

    # GALLERY

    path('gallery-dashboard/', views.gallery_dashboard, name='gallery_dashboard'),
    path('gallery/edit/<int:pk>/', views.gallery_edit, name='gallery_edit'),
    path('gallery/delete/<int:pk>/', views.gallery_delete, name='gallery_delete'),

    path("gallery/", views.gallery, name="gallery"),
    path("exhibitor/", views.exhibitor, name="exhibitor"),
    path("exhibitor-status/", views.exhibitor_status, name="exhibitor_status"),

    # --- Exhibitors management ---
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-dashboard/exhibitors/delete/<uuid:pk>/", views.admin_exhibitor_delete, name="admin_exhibitor_delete"),

    # --- Sections management ---
    path("admin-dashboard/sections/", views.admin_sections, name="admin_sections"),
    path("admin-dashboard/sections/add/", views.admin_add_section, name="add_section"),
    path("admin-dashboard/sections/<int:pk>/edit/", views.admin_edit_section, name="admin_edit_section"),
    path("admin-dashboard/sections/<int:pk>/delete/", views.admin_delete_section, name="admin_delete_section"),

    # --- Booths management ---
    path("admin-dashboard/booths/", views.admin_booths, name="admin_booths"),
    path("admin-dashboard/booths/add/", views.admin_add_booth, name="add_booth"),
    path("admin-dashboard/booths/<int:pk>/edit/", views.admin_edit_booth, name="admin_edit_booth"),
    path("admin-dashboard/booths/<int:pk>/delete/", views.admin_delete_booth, name="delete_booth"),

    # --- sponsor management ---
    path("sponsor/register/", views.summit_sponsor_registration, name="summit_sponsor_registration"),
    path("admin/sponsors/", views.sponsor_dashboard, name="sponsor_dashboard"),
    path("admin/sponsors/delete/<uuid:sponsor_id>/", views.delete_sponsor, name="delete_sponsor"),

    # --- audit & trails ---
    path("audit/apiTrails", views.api_trails, name="api_trails"),
    path("audit/regTrails", views.dashboard_student_view, name="reg_trails"),
    path("audit/approvaTrails", views.dashboard_student_view, name="approve_trails"),

    # --- User Management ---
    path("dashboard/users", views.users, name="users"),
    path("dashboard/add_user", views.add_user, name="add_user"),

    path('dashboard/authregister/', views.save_user, name='save_user'),


    # Badge portal
    path("badge/", views.badge, name="badge"),
    path("auth_badge/", views.auth_badge, name="auth_badge"),
    path("badge_dashboard/", views.badge_dashboard, name="badge_dashboard"),
    path("badge/printed", views.badge_isprinted, name="badge_printed"),
    path("badge/logout/", views.badgeLogout, name="signout"),

    # badge generation
    path("create_badge/<int:reg_id>/", views.create_badge, name="create_badge"),
    path("mark_printed/<int:reg_id>/", views.mark_printed, name="mark_printed"),


]
