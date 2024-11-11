from django.contrib import admin
from .models import Certificate
from django.utils.html import format_html

class CertificateAdmin(admin.ModelAdmin):
    list_display = ('holder_name', 'certificate_id', 'issue_date', 'expiration_date', 'download_pdf_link')
    readonly_fields = ('certificate_id', 'qr_code_image', 'hash_value', 'pdf_file', 'signature_image')
    fields = ('holder_name', 'issue_date', 'expiration_date', 
              'logo', 'signature_text', 'signature_image', 'qr_code_image', 
              'hash_value', 'note', 'pdf_file')
    search_fields = ('holder_name', 'certificate_id')
    list_filter = ('issue_date', 'expiration_date')

    def download_pdf_link(self, obj):
        if obj.pdf_file:
            return format_html('<a href="{}" download>Download PDF</a>', obj.pdf_file.url)
        return "No PDF available"
    download_pdf_link.short_description = "Download PDF"

    def save_model(self, request, obj, form, change):
        # Ensure certificate_id is not manually set, and is auto-generated
        if not obj.certificate_id:
            obj.certificate_id = None  # Set certificate_id to None to ensure it gets auto-generated
        obj.save()  # Calls the model’s save method to regenerate the fields

admin.site.register(Certificate, CertificateAdmin)
