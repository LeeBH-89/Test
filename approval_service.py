import os
from storage import load_json, save_json


REPORT_FILE = os.path.join('data', 'sales_reports.json')

# 허용된 상태 전이 규칙
TRANSITIONS = {
    'DRAFT': ['SUBMITTED'],
    'SUBMITTED': ['APPROVED', 'REJECTED', 'DRAFT'],
}


def _get_transition_name(current_status, new_status):
    """상태 전이에 대응하는 동작 이름을 반환한다."""
    if current_status == 'DRAFT' and new_status == 'SUBMITTED':
        return 'submit'
    if current_status == 'SUBMITTED' and new_status == 'APPROVED':
        return 'approve'
    if current_status == 'SUBMITTED' and new_status == 'REJECTED':
        return 'reject'
    if current_status == 'SUBMITTED' and new_status == 'DRAFT':
        return 'withdraw'
    return None


def transition_status(report_id, new_status):
    """영업일지의 상태를 전이한다.

    Args:
        report_id: 전이할 영업일지 ID
        new_status: 목표 상태

    Returns:
        {'success': True, 'report': dict} 또는
        {'success': False, 'errors': [str]}
    """
    reports = load_json(REPORT_FILE)

    for r in reports:
        if r.get('report_id') == report_id:
            current_status = r.get('status', 'DRAFT')

            # 허용된 전이인지 확인
            allowed = TRANSITIONS.get(current_status, [])
            if new_status not in allowed:
                action = _get_transition_name(current_status, new_status)
                if action:
                    return {
                        'success': False,
                        'errors': [
                            f"'{current_status}' 상태에서 '{action}'을(를) 실행할 수 없습니다."
                        ]
                    }
                return {
                    'success': False,
                    'errors': [
                        f"'{current_status}' 상태에서 '{new_status}'(으)로 전이할 수 없습니다."
                    ]
                }

            r['status'] = new_status
            save_json(REPORT_FILE, reports)
            return {'success': True, 'report': r}

    return {'success': False, 'errors': [f'영업일지 ID {report_id}를 찾을 수 없습니다.']}