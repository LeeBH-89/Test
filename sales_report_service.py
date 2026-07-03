import os
from storage import load_json, save_json
from validators import validate_report_input


REPORT_FILE = os.path.join('data', 'sales_reports.json')
CUSTOMER_FILE = os.path.join('data', 'customers.json')


def _get_next_report_id(reports):
    """가장 큰 report_id + 1 을 반환한다 (예: R001 → R002)."""
    max_num = 0
    for r in reports:
        rid = r.get('report_id', '')
        if rid.startswith('R') and rid[1:].isdigit():
            num = int(rid[1:])
            if num > max_num:
                max_num = num
    return f'R{max_num + 1:03d}'


def _customer_exists(customer_id):
    """주어진 customer_id가 customers.json에 존재하면 True."""
    customers = load_json(CUSTOMER_FILE)
    return any(c.get('customer_id') == customer_id for c in customers)


def register_report(customer_id, activity_date, content):
    """영업일지를 등록하고 등록된 영업일지 dict를 반환한다."""
    errors = validate_report_input(customer_id, activity_date, content)
    if errors:
        return {'success': False, 'errors': errors}

    if not _customer_exists(customer_id.strip()):
        return {'success': False, 'errors': [f'고객사 ID {customer_id.strip()}가 존재하지 않습니다.']}

    reports = load_json(REPORT_FILE)
    new_id = _get_next_report_id(reports)

    new_report = {
        'report_id': new_id,
        'customer_id': customer_id.strip(),
        'activity_date': activity_date.strip(),
        'content': content.strip(),
        'status': 'DRAFT'
    }
    reports.append(new_report)
    save_json(REPORT_FILE, reports)
    return {'success': True, 'report': new_report}


def list_reports():
    """전체 영업일지 목록을 반환한다."""
    return load_json(REPORT_FILE)


def get_report(report_id):
    """특정 영업일지 상세 정보를 반환한다. 없으면 None."""
    reports = load_json(REPORT_FILE)
    for r in reports:
        if r.get('report_id') == report_id:
            return r
    return None


def update_report(report_id, customer_id, activity_date, content):
    """영업일지 정보를 수정한다. APPROVED 상태면 수정을 차단한다."""
    reports = load_json(REPORT_FILE)
    for r in reports:
        if r.get('report_id') == report_id:
            if r.get('status') == 'APPROVED':
                return {'success': False, 'errors': ['APPROVED 상태인 영업일지는 수정할 수 없습니다.']}

            errors = validate_report_input(customer_id, activity_date, content)
            if errors:
                return {'success': False, 'errors': errors}

            if not _customer_exists(customer_id.strip()):
                return {'success': False, 'errors': [f'고객사 ID {customer_id.strip()}가 존재하지 않습니다.']}

            r['customer_id'] = customer_id.strip()
            r['activity_date'] = activity_date.strip()
            r['content'] = content.strip()
            save_json(REPORT_FILE, reports)
            return {'success': True, 'report': r}

    return {'success': False, 'errors': [f'영업일지 ID {report_id}를 찾을 수 없습니다.']}