from django.urls import path
from . import views

app_name = "accounts"
from django.conf import settings
from django.conf.urls.static import static
app_name = "accounts"
urlpatterns = [
    
    
    path('dashboard/superadmin/', views.superadmin_dashboard, name="superadmin_dashboard"),
    path('dashboard/admin/', views.admin_dashboard, name="admin_dashboard"),
    path('dashboard/member/', views.member_dashboard, name="member_dashboard"),

   
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    
    path("profile/", views.profile_update, name="profile_update"),
    path("members/", views.membership_list, name="membership_list"),
    path("change-status/<int:member_id>/<str:new_status>/", views.change_membership_status, name="change_membership_status"),
    path("members/<int:member_id>/update/", views.update_member, name="update_member"),
    path("members/<int:member_id>/promote/", views.promote_member, name="promote_member"),
    path("members/<int:member_id>/demote/", views.demote_member, name="demote_member"),
    path("members/<int:member_id>/activate/", views.activate_member, name="activate_member"),
    path("members/<int:member_id>/deactivate/", views.deactivate_member, name="deactivate_member"),
    path("profile/update/", views.profile_update, name="profile_update"),
    
    path("events/", views.event_list, name="event_list"),
    path("events/create/", views.event_form, name="event_create"),  
    path("events/<int:event_id>/edit/", views.event_form, name="event_edit"),
    path("events/<int:event_id>/delete/", views.event_delete, name="event_delete"),
    path("register-event/<int:event_id>/", views.register_event, name="register_event"),
    path("cancel-event/<int:event_id>/", views.cancel_event, name="cancel_event"),

    
    path("announcements/", views.announcement_list, name="announcement_list"),
    path("announcements/create/", views.create_announcement, name="create_announcement"),
    path("announcements/edit/<int:announcement_id>/", views.announcement_edit, name="edit_announcement"),
    path("announcements/delete/<int:announcement_id>/", views.announcement_delete, name="delete_announcement"),
    path("audit-logs/", views.audit_log_list, name="audit_log_list"),
    path("after-login/", views.redirect_after_login, name="redirect_after_login"),
    

   
    path("add-achievement/", views.add_achievement, name="add_achievement"),
    path("delete-achievement/<int:achievement_id>/", views.delete_achievement, name="delete_achievement"),
    path("view-achievement/<int:id>/", views.view_achievement, name="view_achievement"),
    path('delete-achievement/<int:achievement_id>/', views.delete_achievement, name='delete_achievement'),
    
    path("attendance/scan/<int:event_id>/<str:token>/", views.admin_scan_attendance, name="admin_scan_attendance"),
    path("view-qr/<int:event_id>/", views.view_qr, name="view_qr"),
    path("attendance_report/<int:event_id>/", views.attendance_report_view, name="attendance_report"),
    path("attendance/scan/<int:event_id>/<str:token>/", views.scan_qr_view, name="scan_qr_view"),
    path("scan/<str:qr_code>/", views.scan_qr_view, name="scan_qr_view"),
    path("attendance_report/<int:event_id>/", views.attendance_report_view, name="attendance_report"),
    path("scan/", views.scan_qr_page, name="scan_qr_page"),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)