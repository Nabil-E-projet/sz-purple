#!/usr/bin/env python
"""
Script pour vérifier les fichiers anonymisés après upload d'une fiche de paie.
Usage: python check_anonymization.py <payslip_id>
"""
import os
import json
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'salariz.settings')
django.setup()

from analysis.models import PayslipAnalysis

def check_anonymization(payslip_id):
    print(f"🔍 Vérification de l'anonymisation pour PaySlip ID: {payslip_id}")
    
    try:
        analysis = PayslipAnalysis.objects.get(payslip_id=payslip_id)
        print(f"✅ Analyse trouvée: {analysis.analysis_date}")
        
        # 1. Rapport PII (sans valeurs sensibles)
        if analysis.pii_report:
            print(f"\n📊 PII détectées: {len(analysis.pii_report)} entités")
            for i, pii in enumerate(analysis.pii_report):
                print(f"   {i+1}. Type: {pii['type']}, Score: {pii['score']}, Page: {pii['page']}")
        
        # 2. Extraction minimale
        if analysis.minimal_extract:
            print(f"\n📋 Extraction minimale disponible:")
            extract = analysis.minimal_extract
            print(f"   - Période: {extract.get('periode', {})}")
            print(f"   - Rémunération: {extract.get('remuneration', {})}")
            print(f"   - Convention: {extract.get('convention', {})}")
        
        # 3. PDF masqué
        if analysis.redacted_pdf_path:
            pdf_path = analysis.redacted_pdf_path
            if os.path.exists(pdf_path):
                size = os.path.getsize(pdf_path)
                print(f"\n📄 PDF masqué: {pdf_path}")
                print(f"   - Taille: {size} bytes")
                print(f"   - Vous pouvez l'ouvrir avec: open '{pdf_path}'")
            else:
                print(f"\n❌ PDF masqué non trouvé: {pdf_path}")
        
        # 4. Endpoints API disponibles
        print(f"\n🔗 Endpoints API disponibles:")
        print(f"   GET /api/analysis/payslip/{payslip_id}/pii-report/")
        print(f"   GET /api/analysis/payslip/{payslip_id}/extract.json") 
        print(f"   GET /api/analysis/payslip/{payslip_id}/redacted.pdf")
        
    except PayslipAnalysis.DoesNotExist:
        print(f"❌ Aucune analyse trouvée pour PaySlip {payslip_id}")
        print("   Vérifiez que l'analyse est terminée ou que l'ID est correct.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check_anonymization.py <payslip_id>")
        print("Exemple: python check_anonymization.py 93")
        sys.exit(1)
    
    payslip_id = int(sys.argv[1])
    check_anonymization(payslip_id)
