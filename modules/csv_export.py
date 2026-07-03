import os
import csv
from datetime import datetime
from modules.customer import list_customers

EXPORT_DIR = os.path.join('exports')


def export_customers_to_csv():
    """고객사 목록을 CSV 파일로 내보내고 파일 경로를 반환한다."""
    customers = list_customers()
    if not customers:
        return {'success': False, 'errors': ['내보낼 고객사 데이터가 없습니다.']}

    os.makedirs(EXPORT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'customers_{timestamp}.csv'
    filepath = os.path.join(EXPORT_DIR, filename)

    fieldnames = ['customer_id', 'customer_name', 'manager_name', 'email']
    try:
        with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for c in customers:
                writer.writerow({
                    'customer_id': c.get('customer_id', ''),
                    'customer_name': c.get('customer_name', ''),
                    'manager_name': c.get('manager_name', ''),
                    'email': c.get('email', '')
                })
        return {'success': True, 'filepath': filepath, 'count': len(customers)}
    except OSError as e:
        return {'success': False, 'errors': [f'파일 저장 중 오류가 발생했습니다: {e}']}