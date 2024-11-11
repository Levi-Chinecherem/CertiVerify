from django.shortcuts import render, get_object_or_404
from .models import Certificate
from django.http import HttpResponse
from io import BytesIO
from xhtml2pdf import pisa
from django.template.loader import render_to_string

def certificate_list(request):
    certificates = Certificate.objects.all()
    return render(request, 'certificates/certificate_list.html', {'certificates': certificates})

def download_certificate(request, certificate_id):
    certificate = get_object_or_404(Certificate, certificate_id=certificate_id)

    # Check if the PDF file exists
    if certificate.pdf_file:
        # Serve the existing PDF file
        response = HttpResponse(certificate.pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="certificate_{certificate_id}.pdf"'
        return response
    else:
        # If the PDF file does not exist, return an error
        return HttpResponse("Certificate PDF not found.", status=404)

