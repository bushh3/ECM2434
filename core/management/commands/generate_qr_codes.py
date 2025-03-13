from django.core.management.base import BaseCommand
import qrcode
import os
from django.core.files import File
from core.models import RecyclingBin
from django.conf import settings

class Command(BaseCommand):
    help = "Generate and save QR codes for all recycling bins"

    def handle(self, *args, **kwargs):
        qr_dir = os.path.join(settings.MEDIA_ROOT, "qr_codes")
        os.makedirs(qr_dir, exist_ok=True)

        bins = RecyclingBin.objects.all()
        for bin in bins:
            qr = qrcode.make(bin.qr_code)
            qr_path = os.path.join(qr_dir, f"{bin.qr_code}.png")
            qr.save(qr_path)

            with open(qr_path, "rb") as f:
                bin.qr_code_image.save(f"{bin.qr_code}.png", File(f), save=True)

            self.stdout.write(self.style.SUCCESS(f"QR Code saved: {qr_path}"))