import unittest
import os
import json
from approval_service import transition_status, REPORT_FILE
from sales_report_service import register_report, CUSTOMER_FILE


class TestApprovalService(unittest.TestCase):

    def setUp(self):
        # customers.json 백업
        self._customer_backup = None
        if os.path.exists(CUSTOMER_FILE):
            with open(CUSTOMER_FILE, 'r', encoding='utf-8') as f:
                self._customer_backup = f.read()
        os.makedirs(os.path.dirname(CUSTOMER_FILE), exist_ok=True)
        with open(CUSTOMER_FILE, 'w', encoding='utf-8') as f:
            json.dump([
                {'customer_id': 'C001', 'customer_name': '테스트고객사', 'manager_name': '홍길동', 'email': 'hong@test.com'}
            ], f)

        # sales_reports.json 백업
        self._report_backup = None
        if os.path.exists(REPORT_FILE):
            with open(REPORT_FILE, 'r', encoding='utf-8') as f:
                self._report_backup = f.read()
        os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)

    def tearDown(self):
        # customers.json 복원
        if self._customer_backup is not None:
            with open(CUSTOMER_FILE, 'w', encoding='utf-8') as f:
                f.write(self._customer_backup)
        else:
            if os.path.exists(CUSTOMER_FILE):
                os.remove(CUSTOMER_FILE)

        # sales_reports.json 복원
        if self._report_backup is not None:
            with open(REPORT_FILE, 'w', encoding='utf-8') as f:
                f.write(self._report_backup)
        else:
            if os.path.exists(REPORT_FILE):
                os.remove(REPORT_FILE)

    def _setup_draft_report(self):
        """DRAFT 상태의 영업일지를 등록하고 report_id를 반환한다."""
        result = register_report('C001', '2026-07-03', '테스트 내용')
        self.assertTrue(result['success'])
        return result['report']['report_id']

    def _setup_report_with_status(self, status):
        """지정된 상태의 영업일지를 직접 파일에 기록하고 report_id를 반환한다."""
        reports = [
            {'report_id': 'R001', 'customer_id': 'C001',
             'activity_date': '2026-07-03', 'content': '테스트 내용', 'status': status}
        ]
        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            json.dump(reports, f)
        return 'R001'

    # ---- 정상 전이 ----

    def test_submit_draft(self):
        """DRAFT → SUBMITTED 정상 전이"""
        rid = self._setup_draft_report()
        result = transition_status(rid, 'SUBMITTED')
        self.assertTrue(result['success'])
        self.assertEqual(result['report']['status'], 'SUBMITTED')

    def test_approve_submitted(self):
        """SUBMITTED → APPROVED 정상 전이"""
        rid = self._setup_report_with_status('SUBMITTED')
        result = transition_status(rid, 'APPROVED')
        self.assertTrue(result['success'])
        self.assertEqual(result['report']['status'], 'APPROVED')

    def test_reject_submitted(self):
        """SUBMITTED → REJECTED 정상 전이"""
        rid = self._setup_report_with_status('SUBMITTED')
        result = transition_status(rid, 'REJECTED')
        self.assertTrue(result['success'])
        self.assertEqual(result['report']['status'], 'REJECTED')

    def test_withdraw_submitted(self):
        """SUBMITTED → DRAFT 정상 전이 (철회)"""
        rid = self._setup_report_with_status('SUBMITTED')
        result = transition_status(rid, 'DRAFT')
        self.assertTrue(result['success'])
        self.assertEqual(result['report']['status'], 'DRAFT')

    # ---- 잘못된 전이 ----

    def test_approve_draft_blocked(self):
        """DRAFT 상태에서 승인(approve)은 차단"""
        rid = self._setup_draft_report()
        result = transition_status(rid, 'APPROVED')
        self.assertFalse(result['success'])
        self.assertIn('DRAFT', result['errors'][0])

    def test_submit_approved_blocked(self):
        """APPROVED 상태에서 제출(submit)은 차단"""
        rid = self._setup_report_with_status('APPROVED')
        result = transition_status(rid, 'SUBMITTED')
        self.assertFalse(result['success'])
        self.assertIn('APPROVED', result['errors'][0])

    def test_submit_rejected_blocked(self):
        """REJECTED 상태에서 제출(submit)은 차단"""
        rid = self._setup_report_with_status('REJECTED')
        result = transition_status(rid, 'SUBMITTED')
        self.assertFalse(result['success'])
        self.assertIn('REJECTED', result['errors'][0])

    def test_approve_rejected_blocked(self):
        """REJECTED 상태에서 승인(approve)은 차단"""
        rid = self._setup_report_with_status('REJECTED')
        result = transition_status(rid, 'APPROVED')
        self.assertFalse(result['success'])
        self.assertIn('REJECTED', result['errors'][0])

    def test_reject_approved_blocked(self):
        """APPROVED 상태에서 반려(reject)는 차단"""
        rid = self._setup_report_with_status('APPROVED')
        result = transition_status(rid, 'REJECTED')
        self.assertFalse(result['success'])
        self.assertIn('APPROVED', result['errors'][0])

    def test_reject_draft_blocked(self):
        """DRAFT 상태에서 반려(reject)는 차단"""
        rid = self._setup_draft_report()
        result = transition_status(rid, 'REJECTED')
        self.assertFalse(result['success'])
        self.assertIn('DRAFT', result['errors'][0])

    def test_withdraw_draft_blocked(self):
        """DRAFT 상태에서 철회(withdraw)는 차단"""
        rid = self._setup_draft_report()
        result = transition_status(rid, 'DRAFT')
        self.assertFalse(result['success'])
        self.assertIn('DRAFT', result['errors'][0])

    # ---- 존재하지 않는 ID ----

    def test_transition_not_found(self):
        """존재하지 않는 영업일지 ID로 전이 시도"""
        result = transition_status('R999', 'SUBMITTED')
        self.assertFalse(result['success'])
        self.assertIn('R999', result['errors'][0])

    # ---- APPROVED 상태 수정 차단 유지 확인 ----

    def test_update_approved_still_blocked(self):
        """APPROVED 상태 영업일지 수정 차단(sales_report_service)이 유지되는지 확인"""
        rid = self._setup_report_with_status('APPROVED')
        from sales_report_service import update_report
        result = update_report(rid, 'C001', '2026-07-04', '수정 시도')
        self.assertFalse(result['success'])
        self.assertIn('APPROVED', result['errors'][0])