from django.contrib import admin
from .models import Member, Event, Attendance


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "student_id")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "location", "start_datetime", "end_datetime")


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("user", "event", "status", "timestamp")
    list_filter = ("status", "event")
    search_fields = ("user__username", "event__title")