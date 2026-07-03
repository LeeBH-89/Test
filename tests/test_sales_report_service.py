import unittest
import os
import json
from sales_report_service import (
    register_report, list_reports, get_report, update_report,
    REPORT_FILE, CUSTOMER_FILE
)


class TestSalesReportService(unittest.TestCase):

    def setUp(self):
        # customers.json 백업
        self._customer_backup = None
        if os.path.exists(CUSTOMER_FILE):
            with open(CUSTOMER_FILE, 'r', encoding='utf-8') as f:
                self._customer_backup = f.read()
        os.makedirs(os.path.dirname(CUSTOMER_FILE), exist_ok=True)
        # 테스트용 customers.json: 고객사 C001 하나 등록
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

    # ---- 등록 ----

    def test_register_success(self):
        result = register_report('C001', '2026-07-03', '고객 미팅 진행')
        self.assertTrue(result['success'])
        r = result['report']
        self.assertEqual(r['report_id'], 'R001')
        self.assertEqual(r['customer_id'], 'C001')
        self.assertEqual(r['activity_date'], '2026-07-03')
        self.assertEqual(r['content'], '고객 미팅 진행')
        self.assertEqual(r['status'], 'DRAFT')

    def test_register_id_auto_increment(self):
        r1 = register_report('C001', '2026-07-01', '내용1')
        r2 = register_report('C001', '2026-07-02', '내용2')
        self.assertEqual(r1['report']['report_id'], 'R001')
        self.assertEqual(r2['report']['report_id'], 'R002')

    def test_register_invalid_customer(self):
        result = register_report('C999', '2026-07-03', '내용')
        self.assertFalse(result['success'])
        self.assertIn('C999', result['errors'][0])

    def test_register_empty_customer_id(self):
        result = register_report('', '2026-07-03', '내용')
        self.assertFalse(result['success'])
        self.assertIn('고객사 ID', result['errors'][0])

    def test_register_empty_date(self):
        result = register_report('C001', '', '내용')
        self.assertFalse(result['success'])
        self.assertIn('활동일자', result['errors'][0])

    def test_register_invalid_date_format(self):
        result = register_report('C001', '2026/07/03', '내용')
        self.assertFalse(result['success'])
        self.assertIn('날짜 형식', result['errors'][0])

    def test_register_empty_content(self):
        result = register_report('C001', '2026-07-03', '')
        self.assertFalse(result['success'])
        self.assertIn('활동내용', result['errors'][0])

    # ---- 목록 조회 ----

    def test_list_reports(self):
        register_report('C001', '2026-07-01', '내용1')
        register_report('C001', '2026-07-02', '내용2')
        reports = list_reports()
        self.assertEqual(len(reports), 2)

    def test_list_reports_empty(self):
        reports = list_reports()
        self.assertEqual(len(reports), 0)

    # ---- 상세 조회 ----

    def test_get_report_success(self):
        r = register_report('C001', '2026-07-03', '내용')
        rid = r['report']['report_id']
        report = get_report(rid)
        self.assertIsNotNone(report)
        self.assertEqual(report['report_id'], rid)

    def test_get_report_not_found(self):
        report = get_report('R999')
        self.assertIsNone(report)

    # ---- 수정 ----

    def test_update_success(self):
        r = register_report('C001', '2026-07-03', '내용')
        rid = r['report']['report_id']
        result = update_report(rid, 'C001', '2026-07-04', '수정된 내용')
        self.assertTrue(result['success'])
        self.assertEqual(result['report']['activity_date'], '2026-07-04')
        self.assertEqual(result['report']['content'], '수정된 내용')

    def test_update_not_found(self):
        result = update_report('R999', 'C001', '2026-07-03', '내용')
        self.assertFalse(result['success'])
        self.assertIn('R999', result['errors'][0])

    def test_update_approved_blocked(self):
        """APPROVED 상태인 영업일지는 수정이 차단되어야 한다."""
        # 직접 APPROVED 상태로 저장
        reports = [
            {'report_id': 'R001', 'customer_id': 'C001',
             'activity_date': '2026-07-03', 'content': '원본 내용', 'status': 'APPROVED'}
        ]
        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            json.dump(reports, f)

        result = update_report('R001', 'C001', '2026-07-04', '수정 시도')
        self.assertFalse(result['success'])
        self.assertIn('APPROVED', result['errors'][0])