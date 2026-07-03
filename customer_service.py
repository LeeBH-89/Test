import os
from storage import load_json, save_json
from validators import validate_customer_input


CUSTOMER_FILE = os.path.join('data', 'customers.json')


def _get_next_customer_id(customers):
    """가장 큰 customer_id + 1 을 반환한다 (예: C001 → C002)."""
    max_num = 0
    for c in customers:
        cid = c.get('customer_id', '')
        if cid.startswith('C') and cid[1:].isdigit():
            num = int(cid[1:])
            if num > max_num:
                max_num = num
    return f'C{max_num + 1:03d}'


def register_customer(name, manager, email):
    """신규 고객사를 등록하고 등록된 고객사 dict를 반환한다."""
    errors = validate_customer_input(name, manager, email)
    if errors:
        return {'success': False, 'errors': errors}

    customers = load_json(CUSTOMER_FILE)
    new_id = _get_next_customer_id(customers)

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


def update_customer(customer_id, name, manager, email):
    """고객사 정보를 수정한다."""
    errors = validate_customer_input(name, manager, email)
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