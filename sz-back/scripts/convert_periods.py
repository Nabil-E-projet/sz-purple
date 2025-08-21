import os
import django
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'salariz.settings')
django.setup()

from documents.models import PaySlip

def convert_period_to_date():
    """Convertit les périodes textuelles en dates pour les fiches existantes"""
    payslips = PaySlip.objects.all()
    
    for payslip in payslips:
        if not payslip.period:
            continue
            
        # Traiter différents formats possibles
        try:
            # Cas "01/04/2024 - 30/04/2024" → prendre le 1er jour du mois
            if ' - ' in payslip.period:
                start_date = payslip.period.split(' - ')[0]
                day, month, year = start_date.split('/')
                payslip.period_date = datetime.date(int(year), int(month), int(day))
            # Cas "Avril 2024" → prendre le 1er du mois
            elif ' ' in payslip.period:
                month_name, year = payslip.period.split(' ')
                month_map = {'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6,
                           'juillet': 7, 'août': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12}
                month = month_map.get(month_name.lower(), 1)
                payslip.period_date = datetime.date(int(year), month, 1)
            
            payslip.save(update_fields=['period_date'])
            print(f"Converti: {payslip.period} → {payslip.period_date}")
        except Exception as e:
            print(f"Erreur conversion {payslip.id} ({payslip.period}): {str(e)}")

if __name__ == "__main__":
    convert_period_to_date()