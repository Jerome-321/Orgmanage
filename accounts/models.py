# accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

ROLE_CHOICES = (
    ('superadmin', 'superadmin'),
    ('admin', 'admin'),
    ('member', 'member'),
)

MEMBERSHIP_STATUS = (
    ('active', 'Active'),
    ('inactive', 'Inactive'),
    ('alumni', 'Alumni'),
)


class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    course = models.CharField(max_length=100, null=True, blank=True)
    year = models.CharField(max_length=10, null=True, blank=True)
    role = models.CharField(
        max_length=20,
        choices=[
            ('superadmin', 'superadmin'),
            ('admin', 'admin'),
            ('member', 'member'),
        ],
        default='member'
    )
    status = models.CharField(
        max_length=10,
        choices=[
            ('active', 'active'),
            ('inactive', 'inactive'),
        ],
        default='active'
    )
    joined_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    achievements = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        
        if not self.student_id:
            last_member = Member.objects.order_by('-id').first()
            next_num = 1 if not last_member else last_member.id + 1
            self.student_id = f"STU{next_num:04d}"  
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} ({self.student_id})"

class MembershipHistory(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="history")
    prev_status = models.CharField(max_length=20, choices=MEMBERSHIP_STATUS)
    new_status = models.CharField(max_length=20, choices=MEMBERSHIP_STATUS)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.member.user.username}: {self.prev_status} → {self.new_status}"


class Event(models.Model):
    title = models.CharField(max_length=200)
    start_datetime = models.DateTimeField(default=timezone.now)
    end_datetime = models.DateTimeField(default=timezone.now)
    location = models.CharField(max_length=255, default="TBA")
    max_slots = models.PositiveIntegerField(default=200)
    description = models.TextField(blank=True, null=True)

    def slots_remaining(self):
        
        return self.max_slots - self.registrations.count()

    def total_registered(self):
        
        return self.registrations.count()

    def is_registered_by(self, user):
        
        return self.registrations.filter(user=user).exists()

    def __str__(self):
        return self.title

class EventRegistration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registrations")
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')  

    def __str__(self):
        return f"{self.user.username} registered for {self.event.title}"



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

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True) 

    def __str__(self):
        return f"{self.user.username}'s profile"


@receiver(post_save, sender=User)
def create_member_for_new_user(sender, instance, created, **kwargs):

    if created:
        Member.objects.create(user=instance)  

@receiver(post_save, sender=User)
def save_member_profile(sender, instance, **kwargs):
    if hasattr(instance, 'member'):
        member = instance.member
        
        if not Member.objects.filter(pk=member.pk).exists():
            return  
        member.save(update_fields=["user"])  



class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default="Absent")
    qr_code = models.CharField(max_length=255, unique=True)
    timestamp = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)
    
    STATUS_CHOICES = [
        ("Present", "Present"),
        ("Late", "Late"),
        ("Absent", "Absent"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="attendances"
    )
    event = models.ForeignKey(
        "Event",
        on_delete=models.CASCADE,
        related_name="attendances"
    )
    qr_code = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Absent"
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "event")
        ordering = ("-timestamp",)

    def __str__(self):
        return f"{self.user} - {self.event} ({self.status})"

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
