from ipware import get_client_ip
from .models import RequestLog
import threading

class IPLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Defer logging to a thread to avoid blocking the response
        threading.Thread(target=self.log_request, args=(request,)).start()

        return response

    def log_request(self, request):
        ip, _ = get_client_ip(request)
        if ip is not None:
            RequestLog.objects.create(
                ip_address=ip,
                path=request.path
            )
