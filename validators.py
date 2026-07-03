import re


def validate_customer_input(name, manager, email):
    """고객사 입력값을 검증한다. 오류 메시지 리스트를 반환한다."""
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


def validate_report_input(customer_id, activity_date, content):
    """영업일지 입력값을 검증한다. 오류 메시지 리스트를 반환한다."""
    errors = []
    if not customer_id or not customer_id.strip():
        errors.append('고객사 ID는 필수 입력입니다.')
    if not activity_date or not activity_date.strip():
        errors.append('활동일자는 필수 입력입니다.')
    elif not re.match(r'^\d{4}-\d{2}-\d{2}$', activity_date.strip()):
        errors.append('날짜 형식이 올바르지 않습니다. (YYYY-MM-DD)')
    if not content or not content.strip():
        errors.append('활동내용은 필수 입력입니다.')
    return errors