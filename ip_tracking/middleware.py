from ipware import get_client_ip
from .models import RequestLog, BlockedIP
import threading
from django.http import HttpResponseForbidden

class IPLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip, _ = get_client_ip(request)

        # Check if the IP is blacklisted
        if ip and BlockedIP.objects.filter(ip_address=ip).exists():
            return HttpResponseForbidden("Access denied: your IP has been blocked.")

        # Proceed normally and log in background
        response = self.get_response(request)
        threading.Thread(target=self.log_request, args=(ip, request.path)).start()
        return response

    def log_request(self, ip, path):
        if ip:
            RequestLog.objects.create(
                ip_address=ip,
                path=path
            )
