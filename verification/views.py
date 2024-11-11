from django.shortcuts import render
from django.http import HttpResponse
from certificates.models import Certificate
import fitz  # PyMuPDF for PDF handling
import cv2
import numpy as np
import tempfile

def verify_certificate(request):
    if request.method == 'POST' and 'certificate_image' in request.FILES:
        certificate_pdf = request.FILES['certificate_image']
        
        # Save uploaded PDF temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(certificate_pdf.read())
            temp_pdf_path = temp_pdf.name

        # Convert PDF to image using PyMuPDF (increase resolution by scaling matrix)
        pdf_document = fitz.open(temp_pdf_path)
        page = pdf_document.load_page(0)  # Load the first page

        # Increase the resolution of the image (zoom factor of 2x)
        zoom_matrix = fitz.Matrix(2, 2)  # Zoom factor 2x
        pix = page.get_pixmap(matrix=zoom_matrix)  # Apply zoom matrix
        image = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)

        # Convert to grayscale for QR detection
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply thresholding to improve image quality (use binary thresholding)
        _, thresholded_image = cv2.threshold(gray_image, 128, 255, cv2.THRESH_BINARY)

        # Debugging: Save the thresholded image to check its quality (you can remove this later)
        debug_image_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
        cv2.imwrite(debug_image_path, thresholded_image)
        print(f"Debug image saved at: {debug_image_path}")  # Check the output for debugging

        # Detect and decode the QR code
        qr_detector = cv2.QRCodeDetector()
        extracted_data, points, _ = qr_detector.detectAndDecode(thresholded_image)

        pdf_document.close()

        # If QR code data is found, verify certificate
        if extracted_data:
            print(f"Extracted data: {extracted_data}")  # Debug the extracted QR code data

            # Expecting format like 'certificate_id:hash_value'
            try:
                certificate_id, hash_value = extracted_data.split(":")
                certificate = Certificate.objects.get(certificate_id=certificate_id, hash_value=hash_value)
                return render(request, 'verification/result.html', {
                    'status': 'success',
                    'message': 'Certificate is valid.',
                    'holder_name': certificate.holder_name,
                    'issue_date': certificate.issue_date,
                    'expiration_date': certificate.expiration_date,
                })
            except (Certificate.DoesNotExist, ValueError):
                return render(request, 'verification/result.html', {
                    'status': 'error',
                    'message': 'Certificate not found or may be counterfeit.',
                })
        else:
            return render(request, 'verification/result.html', {
                'status': 'error',
                'message': 'No QR code found in the uploaded file.',
            })

    return render(request, 'verification/verify.html')
