# accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone# -----------------------
# Role and Membership
# -----------------------
ROLE_CHOICES = (
    ('superadmin', 'Superadmin'),
    ('admin', 'Admin'),
    ('member', 'Member'),
)

MEMBERSHIP_STATUS = (
    ('active', 'Active'),
    ('inactive', 'Inactive'),
    ('alumni', 'Alumni'),
)

class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True, null=True, blank=True)  # 👈 add this
    course = models.CharField(max_length=100, null=True, blank=True)
    year = models.CharField(max_length=10, null=True, blank=True)
    role = models.CharField(max_length=20, choices=[
        ('superadmin', 'Superadmin'),
        ('admin', 'Admin'),
        ('member', 'Member'),
    ], default='member')
    status = models.CharField(max_length=10, choices=[
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ], default='active')
    joined_date = models.DateTimeField(auto_now_add=True)
    achievements = models.TextField(blank=True, null=True)
    joined_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    def __str__(self):
        return self.user.username


class MembershipHistory(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="history")
    prev_status = models.CharField(max_length=20, choices=MEMBERSHIP_STATUS)
    new_status = models.CharField(max_length=20, choices=MEMBERSHIP_STATUS)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.member.user.username}: {self.prev_status} → {self.new_status}"

# -----------------------
# Event & Registration
# -----------------------
class Event(models.Model):
    title = models.CharField(max_length=200)
    start_datetime = models.DateTimeField(default=timezone.now)
    end_datetime = models.DateTimeField(default=timezone.now)
    location = models.CharField(max_length=255, default="TBA")
    max_slots = models.PositiveIntegerField(default=50)
    description = models.TextField(blank=True, null=True)

    def slots_remaining(self):
        return self.max_slots - self.registrations.count()

    def is_registered_by(self, user):
        return self.registrations.filter(user=user).exists()

class EventRegistration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registrations")
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')  

    def __str__(self):
        return f"{self.user.username} registered for {self.event.title}"

# -----------------------
# Announcements
# -----------------------
class Announcement(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    def teaser(self):
        return (self.content[:100] + "...") if len(self.content) > 100 else self.content
    def __str__(self):
        return self.title
    def is_new(self, user):
        from datetime import timedelta, timezone, datetime
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        unread = not AnnouncementRead.objects.filter(user=user, announcement=self).exists()
        return self.created_at >= seven_days_ago or unread


class AnnouncementRead(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "announcement")
        

# -----------------------
# Audit Logs
# -----------------------
class AuditLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255)
    target = models.CharField(max_length=255, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.user:
            return f"{self.timestamp} — {self.user.username}: {self.action} ({self.target})"
        return f"{self.timestamp} — System: {self.action} ({self.target})"


class ActionLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    target_member = models.ForeignKey(
        "Member", on_delete=models.CASCADE, null=True, blank=True
    )
    target_announcement = models.ForeignKey(
        "Announcement", on_delete=models.CASCADE, null=True, blank=True
    )

    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.timestamp}: {self.user} — {self.action}"

# -----------------------
# Profile 
# -----------------------
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)  # optional field

    def __str__(self):
        return f"{self.user.username}'s profile"


@receiver(post_save, sender=User)
def create_member_for_new_user(sender, instance, created, **kwargs):
    """Ensure each User has a Member row."""
    if created:
        Member.objects.create(user=instance)  # default role = 'member'

@receiver(post_save, sender=User)
def save_member_profile(sender, instance, **kwargs):
    """Save Member when User is saved (optional but handy)."""
    if hasattr(instance, 'member'):
        instance.member.save()

# -----------------------
# ATTENDANCE
# -----------------------

class Attendance(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="attendances")
    event = models.ForeignKey("Event", on_delete=models.CASCADE, related_name="attendances")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "event")
        ordering = ("-timestamp",)

    def __str__(self):
        return f"{self.user} - {self.event} @ {self.timestamp}"

class Achievement(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="achievements"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    date_earned = models.DateField(default=timezone.now)
    certificate = models.FileField(upload_to='certificates/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.title} - {self.user.username}"
