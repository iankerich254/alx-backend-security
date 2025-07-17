from django.core.cache import cache
from ipware import get_client_ip
from .models import RequestLog, BlockedIP
import threading
from django.http import HttpResponseForbidden
import requests
import os

IPINFO_TOKEN = os.getenv("IPINFO_TOKEN", "your_token_here")  # Replace or use dotenv

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
        country = city = None

        if ip:
            cache_key = f"geo:{ip}"
            geo_data = cache.get(cache_key)

            if not geo_data:
                try:
                    res = requests.get(f"https://ipinfo.io/{ip}/json?token={IPINFO_TOKEN}", timeout=5)
                    if res.status_code == 200:
                        data = res.json()
                        country = data.get("country")
                        city = data.get("city")
                        cache.set(cache_key, {"country": country, "city": city}, 86400)  # Cache 24 hours
                except requests.RequestException:
                    pass
            else:
                country = geo_data.get("country")
                city = geo_data.get("city")

            # Save request log with geo
            RequestLog.objects.create(
                ip_address=ip,
                path=path,
                country=country,
                city=city
            )
