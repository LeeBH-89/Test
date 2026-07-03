import os
from datetime import datetime
from modules import load_json, save_json
from modules.customer import get_customer

REPORT_FILE = os.path.join('data', 'sales_reports.json')


def get_next_report_id(reports):
    """가장 큰 report_id + 1 을 반환한다 (예: R001 → R002)."""
    max_num = 0
    for r in reports:
        rid = r.get('report_id', '')
        if rid.startswith('R') and rid[1:].isdigit():
            num = int(rid[1:])
            if num > max_num:
                max_num = num
    return f'R{max_num + 1:03d}'


def _validate_date(date_str):
    """YYYY-MM-DD 형식과 실제 존재하는 날짜인지 검증한다."""
    if not date_str or not date_str.strip():
        return False
    date_str = date_str.strip()
    parts = date_str.split('-')
    if len(parts) != 3:
        return False
    if len(parts[0]) != 4 or len(parts[1]) != 2 or len(parts[2]) != 2:
        return False
    try:
        datetime(int(parts[0]), int(parts[1]), int(parts[2]))
        return True
    except (ValueError, TypeError):
        return False


def _validate_input(customer_id, date, content):
    """입력값 검증. 오류 메시지 리스트를 반환한다."""
    errors = []

    if not customer_id or not customer_id.strip():
        errors.append('고객사 ID는 필수 입력입니다.')
    elif not customer_id.strip().startswith('C'):
        errors.append('고객사 ID는 C로 시작해야 합니다.')
    else:
        customer = get_customer(customer_id.strip())
        if customer is None:
            errors.append(f'고객사 ID {customer_id.strip()}가 존재하지 않습니다.')

    if not date or not date.strip():
        errors.append('활동일자는 필수 입력입니다.')
    elif not _validate_date(date):
        errors.append('활동일자 형식이 올바르지 않습니다. (YYYY-MM-DD 형식)')

    if not content or not content.strip():
        errors.append('활동내용은 필수 입력입니다.')

    return errors


def register_report(customer_id, date, content):
    """신규 영업일지를 등록하고 등록된 영업일지 dict를 반환한다."""
    errors = _validate_input(customer_id, date, content)
    if errors:
        return {'success': False, 'errors': errors}

    reports = load_json(REPORT_FILE)
    new_id = get_next_report_id(reports)

    new_report = {
        'report_id': new_id,
        'customer_id': customer_id.strip(),
        'activity_date': date.strip(),
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


def update_report(report_id, date, content):
    """영업일지 내용을 수정한다. DRAFT 상태만 수정 가능."""
    if not date or not date.strip():
        return {'success': False, 'errors': ['활동일자는 필수 입력입니다.']}
    if not _validate_date(date):
        return {'success': False, 'errors': ['활동일자 형식이 올바르지 않습니다. (YYYY-MM-DD 형식)']}
    if not content or not content.strip():
        return {'success': False, 'errors': ['활동내용은 필수 입력입니다.']}

    reports = load_json(REPORT_FILE)
    for r in reports:
        if r.get('report_id') == report_id:
            if r.get('status') != 'DRAFT':
                return {'success': False, 'errors': ['DRAFT 상태에서만 수정할 수 있습니다.']}
            r['activity_date'] = date.strip()
            r['content'] = content.strip()
            save_json(REPORT_FILE, reports)
            return {'success': True, 'report': r}

    return {'success': False, 'errors': [f'영업일지 ID {report_id}를 찾을 수 없습니다.']}


def submit_report(report_id):
    """영업일지를 상신한다. DRAFT → SUBMITTED"""
    reports = load_json(REPORT_FILE)
    for r in reports:
        if r.get('report_id') == report_id:
            if r.get('status') != 'DRAFT':
                return {'success': False, 'errors': ['DRAFT 상태에서만 상신할 수 있습니다.']}
            r['status'] = 'SUBMITTED'
            save_json(REPORT_FILE, reports)
            return {'success': True, 'report': r}
    return {'success': False, 'errors': [f'영업일지 ID {report_id}를 찾을 수 없습니다.']}


def approve_report(report_id):
    """영업일지를 승인한다. SUBMITTED → APPROVED"""
    reports = load_json(REPORT_FILE)
    for r in reports:
        if r.get('report_id') == report_id:
            if r.get('status') != 'SUBMITTED':
                return {'success': False, 'errors': ['SUBMITTED 상태에서만 승인할 수 있습니다.']}
            r['status'] = 'APPROVED'
            save_json(REPORT_FILE, reports)
            return {'success': True, 'report': r}
    return {'success': False, 'errors': [f'영업일지 ID {report_id}를 찾을 수 없습니다.']}


def reject_report(report_id):
    """영업일지를 반려한다. SUBMITTED → REJECTED"""
    reports = load_json(REPORT_FILE)
    for r in reports:
        if r.get('report_id') == report_id:
            if r.get('status') != 'SUBMITTED':
                return {'success': False, 'errors': ['SUBMITTED 상태에서만 반려할 수 있습니다.']}
            r['status'] = 'REJECTED'
            save_json(REPORT_FILE, reports)
            return {'success': True, 'report': r}
    return {'success': False, 'errors': [f'영업일지 ID {report_id}를 찾을 수 없습니다.']}


def withdraw_report(report_id):
    """영업일지를 회수한다. SUBMITTED → DRAFT"""
    reports = load_json(REPORT_FILE)
    for r in reports:
        if r.get('report_id') == report_id:
            if r.get('status') != 'SUBMITTED':
                return {'success': False, 'errors': ['SUBMITTED 상태에서만 회수할 수 있습니다.']}
            r['status'] = 'DRAFT'
            save_json(REPORT_FILE, reports)
            return {'success': True, 'report': r}
    return {'success': False, 'errors': [f'영업일지 ID {report_id}를 찾을 수 없습니다.']}
