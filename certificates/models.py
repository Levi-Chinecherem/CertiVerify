from django.db import models
import hashlib
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont
from django.core.files import File
from django.conf import settings
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
import os
from reportlab.pdfbase import pdfmetrics  # Import pdfmetrics for font metrics
import uuid  # Importing uuid to generate unique IDs

class Certificate(models.Model):
    holder_name = models.CharField(max_length=255)
    certificate_id = models.CharField(max_length=100, unique=True, blank=True, null=True)  # Set to blank=True for auto generation
    issue_date = models.DateField(default=timezone.now)
    expiration_date = models.DateField(null=True, blank=True)
    logo = models.ImageField(upload_to='certificates/logos/', null=True, blank=True)
    signature_text = models.CharField(max_length=255, default="Authorized Signature")
    hash_value = models.CharField(max_length=64, blank=True, null=True)
    qr_code_image = models.ImageField(upload_to='certificates/qrcodes/', null=True, blank=True)
    signature_image = models.ImageField(upload_to='certificates/signatures/', null=True, blank=True)
    note = models.TextField(default="This certificate serves as a testament to the dedication, knowledge, and achievements of the holder. It is a mark of excellence, symbolizing the hard work and commitment demonstrated throughout the course of their journey. Congratulations on reaching this milestone.")
    pdf_file = models.FileField(upload_to='certificates/pdfs/', null=True, blank=True)

    def save(self, *args, **kwargs):
        # Auto-generate certificate_id if not provided
        if not self.certificate_id:
            self.certificate_id = str(uuid.uuid4())  # Generating a unique ID using uuid
        self.hash_value = self.generate_certificate_hash()
        self.generate_qr_code()
        self.generate_signature_image()
        self.pdf_file.save(f'{self.certificate_id}_certificate.pdf', self.generate_pdf(), save=False)
        super().save(*args, **kwargs)

    def generate_certificate_hash(self):
        hash_string = f"{self.holder_name}{self.certificate_id}{self.issue_date}"
        return hashlib.sha256(hash_string.encode()).hexdigest()

    def generate_qr_code(self):
        qr = qrcode.make(f'{self.certificate_id}:{self.hash_value}')
        qr_image = BytesIO()
        qr.save(qr_image)
        qr_image.seek(0)
        self.qr_code_image.save(f'{self.certificate_id}_qr.png', ContentFile(qr_image.read()), save=False)

    def generate_signature_image(self):
        signature_text = self.signature_text
        font_path = os.path.join(settings.BASE_DIR, 'static/fonts/CedarvilleCursive-Regular.ttf')  # Make sure the font is in your static folder
        font_size = 40

        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            font = ImageFont.load_default()

        # Use getbbox instead of getsize
        bbox = font.getbbox(signature_text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        image = Image.new("RGBA", (text_width + 20, text_height + 20), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        draw.text((10, 10), signature_text, font=font, fill="black")

        signature_image_file = BytesIO()
        image.save(signature_image_file, format='PNG')
        signature_image_file.seek(0)
        self.signature_image.save(f'{self.certificate_id}_signature.png', ContentFile(signature_image_file.read()), save=False)

    def generate_pdf(self):
        buffer = BytesIO()
        pdf_canvas = canvas.Canvas(buffer, pagesize=landscape(A4))  # Use landscape A4
        width, height = landscape(A4)

        # Title
        pdf_canvas.setFont("Helvetica-Bold", 24)
        pdf_canvas.drawCentredString(width / 2, height - 100, "Certificate of Completion")
        
        # Certificate Holder
        pdf_canvas.setFont("Helvetica", 16)
        pdf_canvas.drawCentredString(width / 2, height - 140, f"This certificate is presented to")
        pdf_canvas.drawCentredString(width / 2, height - 180, self.holder_name)

        # Certificate ID and Dates
        pdf_canvas.setFont("Helvetica", 12)
        pdf_canvas.drawString(100, height - 220, f"Certificate ID: {self.certificate_id}")
        pdf_canvas.drawString(100, height - 240, f"Issue Date: {self.issue_date}")
        if self.expiration_date:
            pdf_canvas.drawString(100, height - 260, f"Expiration Date: {self.expiration_date}")

        # QR Code
        if self.qr_code_image:
            pdf_canvas.drawImage(self.qr_code_image.path, width - 200, height - 300, width=150, height=150)  # Increased QR size

        # Signature Image
        if self.signature_image:
            pdf_canvas.drawImage(self.signature_image.path, 100, height - 350, width=200, height=70)

        # Note Text (Handle overflow by adding line breaks)
        pdf_canvas.setFont("Helvetica-Oblique", 10)
        max_width = width - 200
        lines = self.wrap_text(self.note, max_width)
        y_position = height - 400
        for line in lines:
            pdf_canvas.drawString(100, y_position, line)
            y_position -= 15  # Move to the next line

        pdf_canvas.save()
        buffer.seek(0)
        return ContentFile(buffer.read())

    def wrap_text(self, text, max_width):
        """ Wrap text to fit within the given width. """
        font = "Helvetica-Oblique"
        lines = []
        words = text.split(" ")
        current_line = words[0]
        
        for word in words[1:]:
            test_line = current_line + " " + word
            width = pdfmetrics.stringWidth(test_line, "Helvetica-Oblique", 10)  # Font size 10
            if width < max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        
        lines.append(current_line)  # Add the last line
        return lines

    def __str__(self):
        return f"Certificate for {self.holder_name} ({self.certificate_id})"
