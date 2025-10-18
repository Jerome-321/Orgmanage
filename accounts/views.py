# accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.db import IntegrityError
from .forms import RegisterForm, ProfileUpdateForm, CustomLoginForm, EventForm, AnnouncementForm 
from .models import Member, Event, EventRegistration, Announcement, AuditLog, Achievement, AnnouncementRead,Attendance, Event, EventRegistration, AuditLog, Attendance
from django.utils import timezone
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.contrib.auth.models import User
from accounts.models import ActionLog
from django.core.paginator import Paginator
import io, base64,qrcode,socket
from io import BytesIO
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.core import signing
from django.conf import settings
from django.apps import apps
from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from django.http import FileResponse, Http404
import os
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! Please log in.")
            return redirect("accounts:login")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})

@login_required
def redirect_after_login(request):
    """Send user to the correct dashboard depending on their role"""
    user = request.user
    if user.is_superuser:
        return redirect("accounts:superadmin_dashboard")
    elif hasattr(user, "member") and user.member.role == "Admin":
        return redirect("accounts:admin_dashboard")
    else:
        return redirect("accounts:member_dashboard")


# --- AUTH VIEWS ---
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            
            Member.objects.get_or_create(
                user=user,
                defaults={"role": "member", "membership_status": "active"},
            )

            messages.success(request, "Registration successful. Please log in.")
            return redirect("accounts:login")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})

def login_view(request):
    """Custom login view with QR display and redirect handling."""
    next_url = request.GET.get("next")

    if request.method == "POST":
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            
            if next_url:
                return redirect(next_url)

            
            if user.is_superuser:
                return redirect("accounts:superadmin_dashboard")
            elif hasattr(user, "member") and user.member.role == "Admin":
                return redirect("accounts:admin_dashboard")
            else:
                return redirect("accounts:member_dashboard")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = CustomLoginForm()

    qr_code = generate_login_qr()

    return render(
        request,
        "accounts/login.html",
        {"form": form, "qr_code": qr_code}
    )
def get_local_ip():
    """Get local machine IP address dynamically."""
    try:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)
    except Exception:
        return "127.0.0.1"

def generate_login_qr():
    """Generate base64 QR code for login using local IP."""
    ip = get_local_ip()
    mark_url = f"http://{ip}:8000/login"
    qr_img = qrcode.make(mark_url)
    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()


def logout_view(request):
    logout(request)
    return redirect("accounts:login")  


    return render(request, "accounts/login.html", {"form": form})
def logout_view(request):
    logout(request)
    return redirect("login")

# --- DASHBOARD & PROFILE ---

@login_required
def superadmin_dashboard(request):
    
    total_members = User.objects.count()
    total_events = Event.objects.count()
    total_announcements = Announcement.objects.count()

    
    events = Event.objects.order_by('start_datetime')[:5]
    announcements = Announcement.objects.order_by('-created_at')[:5]
    logs = AuditLog.objects.order_by('-timestamp')[:5]

    return render(request, 'accounts/superadmin_dashboard.html', {
        'total_members': total_members,
        'total_events': total_events,
        'total_announcements': total_announcements,
        'events': events,
        'announcements': announcements,
        'logs': logs,
    })

    return render(request, "accounts/superadmin_dashboard.html", context)
@login_required
def admin_dashboard(request):
    total_members = User.objects.count()
    total_events = Event.objects.count()
    total_announcements = Announcement.objects.count()

    events = Event.objects.order_by('start_datetime')[:5]
    announcements = Announcement.objects.order_by('-created_at')[:5]
    logs = AuditLog.objects.order_by('-timestamp')[:5]

    context = {
        'total_members': total_members,
        'total_events': total_events,
        'total_announcements': total_announcements,
        'events': events,
        'announcements': announcements,
        'logs': logs,
    }

    return render(request, 'accounts/admin_dashboard.html', context)

@login_required
def member_dashboard(request):
    total_events = Event.objects.count()
    total_announcements = Announcement.objects.count()

    # Fetch initial data
    events = Event.objects.order_by('start_datetime')[:5]
    announcements = Announcement.objects.order_by('-created_at')[:5]
    logs = AuditLog.objects.order_by('-timestamp')[:5]

    return render(request, "accounts/member_dashboard.html", {
        'total_events': total_events,
        'total_announcements': total_announcements,
        'events': events,
        'announcements': announcements,
        'logs': logs,
    })

@login_required
def dashboard(request):
    if request.user.is_superuser:
        return render(request, "accounts/superuser_dashboard.html")
    elif hasattr(request.user, "member") and request.user.member.role == "Admin":
        return render(request, "accounts/admin_dashboard.html")
    else:
        return render(request, "accounts/member_dashboard.html")

@login_required
def profile_update(request):
    user = request.user
    member = getattr(user, "member", None)

    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            if member:
                member.course = request.POST.get("course", member.course)
                member.year = request.POST.get("year", member.year)
                member.status = request.POST.get("status", member.status)
                member.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("accounts:dashboard")
    else:
        form = ProfileUpdateForm(instance=user)

    achievements = Achievement.objects.filter(user=user).order_by('-date_earned')

    return render(
        request,
        "accounts/profile_update.html",
        {
            "form": form,
            "member": member,
            "achievements": achievements,
        },
    )


# --- MEMBERSHIP MANAGEMENT ---

@login_required

def membership_list(request):
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").lower()  
    members = Member.objects.all().select_related("user")

    if q:
        members = members.filter(
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q) |
            Q(user__email__icontains=q) |
            Q(student_id__icontains=q) |
            Q(course__icontains=q)
        )

    if status == "active":
        members = members.filter(status__iexact="active")
    elif status == "inactive":
        members = members.filter(status__iexact="inactive")

    context = {
        "members": members,
        "status_filter": status,  
        "q": q,  
    }
    return render(request, "accounts/membership_list.html", context)


@require_POST
@login_required
def update_member(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    user = member.user   
    if not (request.user.is_superuser or (hasattr(request.user, "member") and request.user.member.role in ["Admin", "superadmin"])):
        messages.error(request, "You are not authorized to edit members.")
        return redirect("accounts:membership_list")

    if request.method == "POST":
        try:
           
            user.first_name = request.POST.get("first_name", user.first_name)
            user.last_name = request.POST.get("last_name", user.last_name)
            user.email = request.POST.get("email", user.email)
            user.save()

            
            member.student_id = request.POST.get("student_id", member.student_id)
            member.course = request.POST.get("course", member.course)
            member.year = request.POST.get("year", member.year)
            member.role = request.POST.get("role", member.role)
            member.status = request.POST.get("membership_status", member.status)
            member.save()

           
            AuditLog.objects.create(
                user=request.user,
                action="update_member",
                target=f"Updated member {user.get_full_name() or user.username}"
            )

            messages.success(request, "Member updated successfully.")
        except Exception as e:
            messages.error(request, f"There was a problem saving the member: {e}")
        
        return redirect("accounts:membership_list")

    messages.error(request, "Invalid request.")
    return redirect("accounts:membership_list")


@login_required
@require_POST
def promote_member(request, member_id):
    if not request.user.is_superuser:
        messages.error(request, "Only superadmins can promote/demote.")
        return redirect("accounts:membership_list")

    member = get_object_or_404(Member, id=member_id)
    old = member.role

  
    if member.role == "member":
        member.role = "admin"
    elif member.role == "admin":
        member.role = "superadmin"
    member.save()

    AuditLog.objects.create(
        user=request.user,
        action="promote_member",
        target=f"Promoted {member.user.get_full_name() or member.user.username} from {old} to {member.role}"
    )

    messages.success(request, f"{member.user.get_full_name() or member.user.username} promoted to {member.role}.")
    return redirect("accounts:membership_list")


@login_required
@require_POST
def demote_member(request, member_id):
    if not request.user.is_superuser:
        messages.error(request, "Only superadmins can promote/demote.")
        return redirect("accounts:membership_list")

    member = get_object_or_404(Member, id=member_id)
    old = member.role

    
    if member.role == "superadmin":
        member.role = "admin"
    elif member.role == "admin":
        member.role = "member"
    member.save()
    AuditLog.objects.create(
        user=request.user,
        action="demote_member",
        target=f"Demoted {member.user.get_full_name() or member.user.username} from {old} to {member.role}"
    )

    messages.success(request, f"{member.user.get_full_name() or member.user.username} demoted to {member.role}.")
    return redirect("accounts:membership_list")

@login_required
@require_POST
def activate_member(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    if not (request.user.is_superuser or (hasattr(request.user, "member") and request.user.member.role in ["Admin","superadmin"])):
        messages.error(request, "You are not authorized.")
        return redirect("accounts:membership_list")
    old = member.membership_status
    member.membership_status = "active"
    member.save()
    ActionLog.objects.create(user=request.user, target_member=member, action=f"Activated {member.user.get_full_name() or member.user.username} (was {old})")
    messages.success(request, f"{member.user.get_full_name() or member.user.username} activated.")
    return redirect("accounts:membership_list")

@login_required
@require_POST
def deactivate_member(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    if not (request.user.is_superuser or (hasattr(request.user, "member") and request.user.member.role in ["Admin","superadmin"])):
        messages.error(request, "You are not authorized.")
        return redirect("accounts:membership_list")
    old = member.membership_status
    member.membership_status = "inactive"
    member.save()
    ActionLog.objects.create(user=request.user, target_member=member, action=f"Deactivated {member.user.get_full_name() or member.user.username} (was {old})")
    messages.success(request, f"{member.user.get_full_name() or member.user.username} deactivated.")
    return redirect("accounts:membership_list")


@login_required
def change_membership_status(request, member_id, new_status):
    member = get_object_or_404(Member, id=member_id)
    if hasattr(request.user, "member") and request.user.member.role in ["Admin", "superadmin"]:
        old_status = member.membership_status
        member.membership_status = new_status
        member.save()
        AuditLog.objects.create(
            user=request.user,
            action="change_membership_status",
            target=f"Changed {member.user.get_full_name() or member.user.username}'s status from {old_status} to {new_status}"
        )

        messages.success(request, f"{member.user.username}'s status updated to {new_status}.")
    else:
        messages.error(request, "You do not have permission to change membership status.")
    return redirect("accounts:membership_list")


# --- EVENTS ---

@login_required
def event_list(request):
    events = Event.objects.annotate(registered_count=Count('registrations'))
    now = timezone.now()

    for e in events:
        e.registered = e.is_registered_by(request.user)
        e.form = EventForm(instance=e)

    return render(request, 'accounts/event_list.html', {
        "events": events,
        "now": now,
    })

@login_required
def event_form(request, event_id=None):
    event = None
    if event_id:
        event = get_object_or_404(Event, id=event_id)

        if request.user.member.role not in ["admin", "superadmin"] and event.created_by != request.user:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"error": "Unauthorized"}, status=403)
            messages.error(request, "You are not authorized to edit this event.")
            return redirect("accounts:event_list")

    if request.method == "POST":
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            new_event = form.save(commit=False)
            if not event:  
                new_event.created_by = request.user
                action = "create_event"
                target = f"Created event '{new_event.title}'"
            else:
                action = "update_event"
                target = f"Updated event '{new_event.title}'"

            new_event.save()

            
            AuditLog.objects.create(
                user=request.user,
                action=action,
                target=target
            )

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": True})

            messages.success(request, f"Event {'updated' if event else 'created'} successfully.")
            return redirect("accounts:event_list")

        else:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"errors": form.errors}, status=400)

    return redirect("accounts:event_list")

@login_required
def event_edit(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.user.member.role not in ["Admin", "superadmin"] and event.created_by != request.user:
        messages.error(request, "You are not authorized to edit this event.")
        return redirect("accounts:event_list")

    if request.method == "POST":
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()

            AuditLog.objects.create(
                user=request.user,
                action="update_event",
                target=f"Edited event '{event.title}'"
            )

            messages.success(request, "Event updated successfully.")
            return redirect("accounts:event_list")
    else:
        form = EventForm(instance=event)

    return render(request, "accounts/event_form.html", {"form": form})


@login_required
def event_delete(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.user.member.role not in ["Admin", "superadmin"] and event.created_by != request.user:
        messages.error(request, "You are not authorized to delete this event.")
        return redirect("accounts:event_list")

    if request.method == "POST":
        title = event.title
        event.delete()

        AuditLog.objects.create(
            user=request.user,
            action="delete_event",
            target=f"Deleted event '{title}'"
        )

        messages.success(request, "Event deleted successfully.")
        return redirect("accounts:event_list")

    return render(request, "accounts/event_confirm_delete.html", {"event": event})

@login_required
def register_event(request, event_id):
    import io, base64, socket, qrcode
    from django.core import signing

    event = get_object_or_404(Event, id=event_id)

    existing_registration = EventRegistration.objects.filter(
        user=request.user, event=event
    ).first()

    if existing_registration:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"status": "already_registered"}, status=400)
        messages.info(request, "You are already registered for this event.")
        return redirect("accounts:event_list")

    EventRegistration.objects.create(user=request.user, event=event)

    AuditLog.objects.create(
        user=request.user,
        action="register_event",
        target=f"Registered for event '{event.title}'"
    )

    payload = {"user_id": request.user.id, "event_id": event.id}
    token = signing.dumps(payload, salt="attendance-salt-v1")

    ip = socket.gethostbyname(socket.gethostname())
    mark_url = f"http://{ip}:8000/attendance/scan/{event.id}/{token}/"

    qr = qrcode.QRCode(box_size=8, border=3)
    qr.add_data(mark_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    qr_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "status": "registered",
            "registered": event.registrations.count(),
            "slots_remaining": event.capacity - event.registrations.count(),
            "qr_url": mark_url
        })

    messages.success(request, f"You have successfully registered for {event.title}!")

    return render(request, "accounts/view_qr.html", {
        "event": event,
        "qr_code": qr_base64,
        "mark_url": mark_url,
    })

@login_required
def cancel_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    registration = EventRegistration.objects.filter(user=request.user, event=event).first()

    if registration:
        registration.delete()

        AuditLog.objects.create(
            user=request.user,
            action="cancel_event",
            target=f"Canceled registration for event '{event.title}'"
        )

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({
                "status": "canceled",
                "registered": event.registrations.count(),
                "slots_remaining": event.capacity - event.registrations.count()
            })

        messages.success(request, f"You have canceled your registration for {event.title}.")
    else:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"status": "not_registered"}, status=400)
        messages.warning(request, "You are not registered for this event.")

    return redirect("accounts:event_list")

# --- ANNOUNCEMENTS ---

@login_required
def announcement_list(request):
    announcements = Announcement.objects.order_by("-created_at")
    read_ids = AnnouncementRead.objects.filter(user=request.user).values_list("announcement_id", flat=True)

    for ann in announcements:
        ann.is_new = (ann.created_at >= timezone.now() - timezone.timedelta(days=7)) or (ann.id not in read_ids)
        ann.teaser = ann.content[:100] + ("..." if len(ann.content) > 100 else "")

    return render(request, "accounts/announcement_list.html", {"announcements": announcements})

@login_required
def create_announcement(request):
    if not (request.user.is_superuser or hasattr(request.user, "member") and request.user.member.role in ["Admin", "superadmin"]):
        messages.error(request, "You are not authorized to create announcements.")
        return redirect("accounts:announcement_list")

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()

        if not title or not content:
            messages.error(request, "Title and content are required.")
            return redirect("accounts:announcement_list")

        ann = Announcement.objects.create(
            title=title,
            content=content,
            author=request.user
        )

        AuditLog.objects.create(
            user=request.user,
            action="create_announcement",
            target=f"Created announcement '{ann.title}'"
        )

        messages.success(request, "Announcement created successfully.")
        return redirect("accounts:announcement_list")

    return redirect("accounts:announcement_list")

@login_required
def announcement_edit(request, announcement_id):
    announcement = get_object_or_404(Announcement, id=announcement_id)

    if not (request.user.is_superuser or (hasattr(request.user, "member") and request.user.member.role in ["Admin", "superadmin"])):
        messages.error(request, "You are not authorized to edit announcements.")
        return redirect("accounts:announcement_list")

    if request.method == "POST":
        form = AnnouncementForm(request.POST, instance=announcement)
        if form.is_valid():
            form.save()

            AuditLog.objects.create(
                user=request.user,
                action="update_announcement",
                target=f"Edited announcement '{announcement.title}'"
            )

            messages.success(request, "Announcement updated successfully.")
            return redirect("accounts:announcement_list")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AnnouncementForm(instance=announcement)

    return render(request, "accounts/announcement_edit.html", {"form": form, "announcement": announcement})


@login_required
@user_passes_test(lambda u: u.is_superuser or (hasattr(u, "member") and u.member.role in ["Admin", "superadmin"]))
def announcement_delete(request, announcement_id):
    try:
        ann = Announcement.objects.get(id=announcement_id)
    except Announcement.DoesNotExist:
        messages.error(request, "Announcement not found or already deleted.")
        return redirect("accounts:announcement_list")

    if request.method == "POST":
        title = ann.title
        ann.delete()

        AuditLog.objects.create(
            user=request.user,
            action="delete_announcement",
            target=f"Deleted announcement '{title}'"
        )

        messages.success(request, f'Announcement "{title}" deleted successfully.')
        return redirect("accounts:announcement_list")

    return redirect("accounts:announcement_list")


@login_required
def audit_log_list(request):
    logs = AuditLog.objects.all().order_by("-timestamp")

    action = request.GET.get("action", "").strip()
    user = request.GET.get("user", "").strip()
    start_date = request.GET.get("start_date", "")
    end_date = request.GET.get("end_date", "")

    if action:
        logs = logs.filter(action__icontains=action)
    if user:
        logs = logs.filter(user__username__icontains=user)
    if start_date:
        logs = logs.filter(timestamp__gte=start_date)
    if end_date:
        logs = logs.filter(timestamp__lte=end_date)

    logins_count = AuditLog.objects.filter(action__icontains="login").count()
    event_actions_count = AuditLog.objects.filter(action__icontains="event").count()
    profile_updates_count = AuditLog.objects.filter(action__icontains="update profile").count()

    paginator = Paginator(logs, 10)  
    page_number = request.GET.get("page")
    logs_page = paginator.get_page(page_number)

    context = {
        "logs": logs_page,
        "logins_count": logins_count,
        "event_actions_count": event_actions_count,
        "profile_updates_count": profile_updates_count,
        "selected_action": action,
        "selected_user": user,
        "selected_start_date": start_date,
        "selected_end_date": end_date,
    }
    return render(request, "accounts/audit_log_list.html", context)

@login_required
def view_achievement(request, id):
    from .models import Achievement  # import your model

    achievement = get_object_or_404(Achievement, id=id, user=request.user)
    if not achievement.certificate:
        raise Http404("Certificate not found.")

    # Get full path to the certificate file
    file_path = achievement.certificate.path

    if os.path.exists(file_path):
        # Return the file for inline viewing (PDF or image)
        return FileResponse(open(file_path, 'rb'), content_type='application/pdf')
    else:
        raise Http404("File does not exist on server.")
    

def add_achievement(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        date_earned = request.POST.get("date_earned")
        certificate = request.FILES.get("certificate") 

        
        achievement = Achievement.objects.create(
            user=request.user,  
            title=title,
            description=description,
            date_earned=date_earned,
            certificate=certificate
        )

        
        messages.success(request, "Achievement added successfully!")
        return redirect("accounts:profile_update")

    return redirect("accounts:profile_update")


@login_required
def delete_achievement(request, achievement_id):
    achievement = get_object_or_404(Achievement, id=achievement_id, user=request.user)

    if request.method == "POST":
        if achievement.certificate:
            achievement.certificate.delete(save=False)

        achievement.delete()
        messages.success(request, "Achievement deleted successfully.")
        return redirect("accounts:profile_update")

    messages.error(request, "Invalid request.")
    return redirect("accounts:profile_update")


SIGNER_SALT = "attendance-salt-v2"
TOKEN_MAX_AGE_SECONDS = 60 * 60 * 12  # 12 hours

def generate_token(payload: dict) -> str:
    return signing.dumps(payload, salt=SIGNER_SALT)

def load_token(token: str, max_age: int = TOKEN_MAX_AGE_SECONDS) -> dict:
    return signing.loads(token, salt=SIGNER_SALT, max_age=max_age)



@login_required
@login_required
def view_qr(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    if not EventRegistration.objects.filter(event=event, user=request.user).exists():
        return render(request, "accounts/view_qr.html", {
            "event": event,
            "not_registered": True
        })

    payload = {"user_id": request.user.id, "event_id": event.id}
    token = generate_token(payload)
    ip = socket.gethostbyname(socket.gethostname())
    qr_url = f"http://{ip}:8000/attendance/scan/{event.id}/{token}/"

   
    qr = qrcode.QRCode(box_size=8, border=3)
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

   
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, "accounts/view_qr.html", {"event": event, "qr_image": qr_base64})

# --- ADMIN: Scan and mark attendance ---
@login_required
def admin_scan_attendance(request, event_id, token):
    """Admin scans a member’s QR and marks their attendance."""
    if not (request.user.is_superuser or getattr(request.user.member, "role", "").lower() == "Admin"):
        return HttpResponseForbidden("Only admins can scan attendance QR codes.")

    try:
        data = load_token(token)
    except signing.BadSignature:
        return render(request, "accounts/attendance_mark.html", {
            "status": "invalid", "message": "Invalid or corrupted QR code."
        })
    except signing.SignatureExpired:
        return render(request, "accounts/attendance_mark.html", {
            "status": "expired", "message": "This QR code has expired."
        })

    if int(data["event_id"]) != int(event_id):
        return render(request, "accounts/attendance_mark.html", {
            "status": "invalid", "message": "This QR code does not match the event."
        })

    member_id = data["user_id"]
    event = get_object_or_404(Event, pk=event_id)
    member = get_object_or_404(EventRegistration, event=event, user_id=member_id).user


    attendance, created = Attendance.objects.get_or_create(user=member, event=event)
    if created:
        status, message = "ok", f"{member.username}'s attendance has been recorded!"
    else:
        status, message = "already", f"{member.username}'s attendance is already marked."

    return render(request, "accounts/attendance_mark.html", {
        "status": status,
        "message": message,
        "event": event,
    })


@csrf_exempt
def scan_qr_view(request):
    if request.method == 'POST':
        qr_data = request.POST.get('qr_data')
        try:
            attendance = Attendance.objects.get(qr_code=qr_data)
            attendance.status = 'Present'
            attendance.save()
            return JsonResponse({'success': True, 'message': f"{attendance.user.username} marked present!"})
        except Attendance.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'QR code not found.'})
    return JsonResponse({'error': 'Invalid request.'})
def scan_qr(request):
    return render(request, 'accounts/scan_qr.html')
