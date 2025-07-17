from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from ip_tracking.models import RequestLog, SuspiciousIP

SUSPICIOUS_PATHS = ['/admin', '/login']

@shared_task
def detect_suspicious_ips():
    one_hour_ago = timezone.now() - timedelta(hours=1)

    # Group request logs by IP
    logs = RequestLog.objects.filter(timestamp__gte=one_hour_ago)

    ip_counts = {}
    for log in logs:
        ip = log.ip_address
        ip_counts[ip] = ip_counts.get(ip, 0) + 1

        # Check for sensitive path access
        if log.path in SUSPICIOUS_PATHS:
            SuspiciousIP.objects.get_or_create(
                ip_address=ip,
                reason=f"Accessed sensitive path: {log.path}"
            )

    for ip, count in ip_counts.items():
        if count > 100:
            SuspiciousIP.objects.get_or_create(
                ip_address=ip,
                reason=f"More than 100 requests in 1 hour: {count} requests"
            )
