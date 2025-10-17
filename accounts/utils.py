from .models import AuditLog
from django.utils.timezone import now
import socket
import qrcode
from io import BytesIO
import base64
def log_action(user, action, target=None, ip=None):
    """Helper function to record actions in AuditLog."""
    AuditLog.objects.create(
        user=user if user.is_authenticated else None,
        action=action,
        target=target,
        ip_address=ip,
        timestamp=now()
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