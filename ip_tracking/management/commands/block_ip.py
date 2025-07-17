from django.core.management.base import BaseCommand
from ip_tracking.models import BlockedIP

class Command(BaseCommand):
    help = "Block a specific IP address"

    def add_arguments(self, parser):
        parser.add_argument('ip_address', type=str, help='The IP address to block')

    def handle(self, *args, **kwargs):
        ip_address = kwargs['ip_address']
        obj, created = BlockedIP.objects.get_or_create(ip_address=ip_address)
        if created:
            self.stdout.write(self.style.SUCCESS(f"IP address {ip_address} has been blocked."))
        else:
            self.stdout.write(self.style.WARNING(f"IP address {ip_address} is already blocked."))
