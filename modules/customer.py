import os
from modules import load_json, save_json

CUSTOMER_FILE = os.path.join('data', 'customers.json')


def get_next_customer_id(customers):
    """가장 큰 customer_id + 1 을 반환한다 (예: C001 → C002)."""
    max_num = 0
    for c in customers:
        cid = c.get('customer_id', '')
        if cid.startswith('C') and cid[1:].isdigit():
            num = int(cid[1:])
            if num > max_num:
                max_num = num
    return f'C{max_num + 1:03d}'


def _validate_input(name, manager, email):
    """입력값 검증. 오류 메시지 리스트를 반환한다."""
    errors = []
    if not name or not name.strip():
        errors.append('고객사명은 필수 입력입니다.')
    if not manager or not manager.strip():
        errors.append('담당자명은 필수 입력입니다.')
    if not email or not email.strip():
        errors.append('이메일은 필수 입력입니다.')
    elif '@' not in email.strip():
        errors.append('이메일 형식이 올바르지 않습니다. (@가 포함되어야 합니다)')
    return errors


def register_customer(name, manager, email):
    """신규 고객사를 등록하고 등록된 고객사 dict를 반환한다."""
    errors = _validate_input(name, manager, email)
    if errors:
        return {'success': False, 'errors': errors}

    customers = load_json(CUSTOMER_FILE)
    new_id = get_next_customer_id(customers)

    new_customer = {
        'customer_id': new_id,
        'customer_name': name.strip(),
        'manager_name': manager.strip(),
        'email': email.strip()
    }
    customers.append(new_customer)
    save_json(CUSTOMER_FILE, customers)
    return {'success': True, 'customer': new_customer}


def list_customers():
    """전체 고객사 목록을 반환한다."""
    return load_json(CUSTOMER_FILE)


def get_customer(customer_id):
    """특정 고객사 상세 정보를 반환한다. 없으면 None."""
    customers = load_json(CUSTOMER_FILE)
    for c in customers:
        if c.get('customer_id') == customer_id:
            return c
    return None


def search_customers(keyword):
    """고객사명 또는 담당자명에 keyword가 포함된 고객사 목록을 반환한다."""
    if not keyword or not keyword.strip():
        return []
    keyword = keyword.strip().lower()
    customers = load_json(CUSTOMER_FILE)
    result = []
    for c in customers:
        if keyword in c.get('customer_name', '').lower() or \
           keyword in c.get('manager_name', '').lower():
            result.append(c)
    return result


def update_customer(customer_id, name, manager, email):
    """고객사 정보를 수정한다."""
    errors = _validate_input(name, manager, email)
    if errors:
        return {'success': False, 'errors': errors}

    customers = load_json(CUSTOMER_FILE)
    for c in customers:
        if c.get('customer_id') == customer_id:
            c['customer_name'] = name.strip()
            c['manager_name'] = manager.strip()
            c['email'] = email.strip()
            save_json(CUSTOMER_FILE, customers)
            return {'success': True, 'customer': c}

    return {'success': False, 'errors': [f'고객사 ID {customer_id}를 찾을 수 없습니다.']}


def delete_customer(customer_id):
    """고객사를 삭제한다."""
    customers = load_json(CUSTOMER_FILE)
    for i, c in enumerate(customers):
        if c.get('customer_id') == customer_id:
            deleted = customers.pop(i)
            save_json(CUSTOMER_FILE, customers)
            return {'success': True, 'customer': deleted}

    return {'success': False, 'errors': [f'고객사 ID {customer_id}를 찾을 수 없습니다.']}