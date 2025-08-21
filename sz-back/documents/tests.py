# Dans tests.py
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from .models import PaySlip

class PaySlipModelTests(TestCase):
    def test_invalid_file_type(self):
        # Test avec un fichier non-PDF
        with self.assertRaises(ValidationError):
            file = SimpleUploadedFile("document.txt", b"text content", content_type="text/plain")
            payslip = PaySlip(uploaded_file=file)
            payslip.full_clean()