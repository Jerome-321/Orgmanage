from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    
    # Role-based dashboards
    path('dashboard/superadmin/', views.superadmin_dashboard, name="superadmin_dashboard"),
    path('dashboard/admin/', views.admin_dashboard, name="admin_dashboard"),
    path('dashboard/member/', views.member_dashboard, name="member_dashboard"),

    # Authentication
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # Profile & Membership
    path("profile/", views.profile_update, name="profile_update"),
    path("members/", views.membership_list, name="membership_list"),
    path("change-status/<int:member_id>/<str:new_status>/", views.change_membership_status, name="change_membership_status"),
    path("members/<int:member_id>/update/", views.update_member, name="update_member"),
    path("members/<int:member_id>/promote/", views.promote_member, name="promote_member"),
    path("members/<int:member_id>/demote/", views.demote_member, name="demote_member"),
    path("members/<int:member_id>/activate/", views.activate_member, name="activate_member"),
    path("members/<int:member_id>/deactivate/", views.deactivate_member, name="deactivate_member"),

    # Events
    path("events/", views.event_list, name="event_list"),
    path("events/create/", views.event_form, name="event_create"),  # ✅ keep only one
    path("events/<int:event_id>/edit/", views.event_form, name="event_edit"),
    path("events/<int:event_id>/delete/", views.event_delete, name="event_delete"),
    path("register-event/<int:event_id>/", views.register_event, name="register_event"),
    path("cancel-event/<int:event_id>/", views.cancel_event, name="cancel_event"),
    
    # Announcements & Audit Logs
    path("announcements/", views.announcement_list, name="announcement_list"),
    path("announcements/create/", views.create_announcement, name="create_announcement"),
    path("announcements/edit/<int:announcement_id>/", views.announcement_edit, name="edit_announcement"),
    path("announcements/delete/<int:announcement_id>/", views.announcement_delete, name="delete_announcement"),
    path("audit-logs/", views.audit_log_list, name="audit_log_list"),
    path("after-login/", views.redirect_after_login, name="redirect_after_login"),

    # Achievements
    path("add-achievement/", views.add_achievement, name="add_achievement"),

    # Attendance
    path("attendance/scan/<int:event_id>/<str:token>/", views.admin_scan_attendance, name="admin_scan_attendance"),
    path("view-qr/<int:event_id>/", views.view_qr, name="view_qr"),
    path('scan-qr/', views.scan_qr, name='scan_qr'),
]
