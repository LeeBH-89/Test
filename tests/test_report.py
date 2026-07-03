import unittest
import os
import json
from modules.customer import register_customer, CUSTOMER_FILE
from modules.report import (
    register_report, list_reports, get_report, update_report,
    submit_report, approve_report, reject_report, withdraw_report,
    REPORT_FILE
)


class TestReport(unittest.TestCase):

    def setUp(self):
        # backup customers
        self._cust_backup = None
        if os.path.exists(CUSTOMER_FILE):
            with open(CUSTOMER_FILE, 'r', encoding='utf-8') as f:
                self._cust_backup = f.read()
        os.makedirs(os.path.dirname(CUSTOMER_FILE), exist_ok=True)
        with open(CUSTOMER_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)

        # backup reports
        self._report_backup = None
        if os.path.exists(REPORT_FILE):
            with open(REPORT_FILE, 'r', encoding='utf-8') as f:
                self._report_backup = f.read()
        os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)

        # 테스트용 고객사 등록
        r = register_customer('테스트', '관리자', 'admin@t.com')
        self.cid = r['customer']['customer_id']

    def tearDown(self):
        # restore customers
        if self._cust_backup is not None:
            with open(CUSTOMER_FILE, 'w', encoding='utf-8') as f:
                f.write(self._cust_backup)
        else:
            if os.path.exists(CUSTOMER_FILE):
                os.remove(CUSTOMER_FILE)

        # restore reports
        if self._report_backup is not None:
            with open(REPORT_FILE, 'w', encoding='utf-8') as f:
                f.write(self._report_backup)
        else:
            if os.path.exists(REPORT_FILE):
                os.remove(REPORT_FILE)

    def _register_draft(self):
        """DRAFT 상태의 영업일지를 등록하고 report_id를 반환한다."""
        r = register_report(self.cid, '2026-07-03', '테스트 미팅')
        return r['report']['report_id']

    # 1. 영업일지 등록 정상 동작
    def test_register_success(self):
        result = register_report(self.cid, '2026-07-03', '제품 미팅')
        self.assertTrue(result['success'])
        self.assertEqual(result['report']['status'], 'DRAFT')
        self.assertEqual(result['report']['report_id'], 'R001')

    # 2. 잘못된 날짜 형식 차단
    def test_register_invalid_date_format(self):
        result = register_report(self.cid, '2026/07/03', '내용')
        self.assertFalse(result['success'])

    def test_register_invalid_date_not_exist(self):
        result = register_report(self.cid, '2026-13-01', '내용')
        self.assertFalse(result['success'])

    # 3. 존재하지 않는 고객사 ID 차단
    def test_register_invalid_customer(self):
        result = register_report('C999', '2026-07-03', '내용')
        self.assertFalse(result['success'])
        self.assertIn('C999', result['errors'][0])

    # 4. 활동내용 공백 차단
    def test_register_empty_content(self):
        result = register_report(self.cid, '2026-07-03', '')
        self.assertFalse(result['success'])
        self.assertIn('활동내용', result['errors'][0])

    # 5. 전체 목록 조회
    def test_list_reports(self):
        self._register_draft()
        self._register_draft()
        reports = list_reports()
        self.assertEqual(len(reports), 2)

    # 6. 상세 조회 (존재/부재)
    def test_get_report_success(self):
        rid = self._register_draft()
        report = get_report(rid)
        self.assertIsNotNone(report)
        self.assertEqual(report['content'], '테스트 미팅')

    def test_get_report_not_found(self):
        report = get_report('R999')
        self.assertIsNone(report)

    # 7. 수정 정상 동작 (DRAFT)
    def test_update_success(self):
        rid = self._register_draft()
        result = update_report(rid, '2026-07-04', '수정된 내용')
        self.assertTrue(result['success'])
        self.assertEqual(result['report']['activity_date'], '2026-07-04')
        self.assertEqual(result['report']['content'], '수정된 내용')

    # 8. DRAFT가 아닌 상태 수정 차단
    def test_update_not_draft(self):
        rid = self._register_draft()
        submit_report(rid)
        result = update_report(rid, '2026-07-04', '수정 시도')
        self.assertFalse(result['success'])
        self.assertIn('DRAFT', result['errors'][0])

    # 9. 상신 → 승인 정상 흐름
    def test_submit_then_approve(self):
        rid = self._register_draft()
        s = submit_report(rid)
        self.assertTrue(s['success'])
        self.assertEqual(s['report']['status'], 'SUBMITTED')
        a = approve_report(rid)
        self.assertTrue(a['success'])
        self.assertEqual(a['report']['status'], 'APPROVED')

    # 10. 상신 → 반려 정상 흐름
    def test_submit_then_reject(self):
        rid = self._register_draft()
        submit_report(rid)
        r = reject_report(rid)
        self.assertTrue(r['success'])
        self.assertEqual(r['report']['status'], 'REJECTED')

    # 11. 상신 → 회수 정상 흐름
    def test_submit_then_withdraw(self):
        rid = self._register_draft()
        submit_report(rid)
        w = withdraw_report(rid)
        self.assertTrue(w['success'])
        self.assertEqual(w['report']['status'], 'DRAFT')

    # 12. 잘못된 상태 전이 차단
    def test_approve_from_draft(self):
        rid = self._register_draft()
        result = approve_report(rid)
        self.assertFalse(result['success'])

    def test_reject_from_draft(self):
        rid = self._register_draft()
        result = reject_report(rid)
        self.assertFalse(result['success'])

    def test_withdraw_from_draft(self):
        rid = self._register_draft()
        result = withdraw_report(rid)
        self.assertFalse(result['success'])

    def test_submit_from_approved(self):
        rid = self._register_draft()
        submit_report(rid)
        approve_report(rid)
        result = submit_report(rid)
        self.assertFalse(result['success'])


if __name__ == '__main__':
    unittest.main()