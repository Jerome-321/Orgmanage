from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Profile

User = settings.AUTH_USER_MODEL

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
from django.contrib.auth.models import User
from .models import Member

@receiver(post_save, sender=User)
def create_member_for_new_user(sender, instance, created, **kwargs):
    """
    Automatically create a Member whenever a new User is created.
    """
    if created:
        # Check if the user already has a Member (just to be safe)
        if not Member.objects.filter(user=instance).exists():
            Member.objects.create(user=instance)
            print(f"✅ Member created for user: {instance.username}")


@receiver(post_save, sender=Member)
def create_user_for_new_member(sender, instance, created, **kwargs):
    """
    Automatically create a matching User if a Member is manually added via Admin.
    """
    if created and not instance.user_id:
        username = instance.student_id or f"auto_user_{instance.id}"
        user = User.objects.create(username=username)
        instance.user = user
        instance.save()
        print(f"✅ User created for new member: {username}")
