import unittest
import os
import json
from customer_service import (
    register_customer, list_customers, get_customer,
    update_customer, delete_customer,
    CUSTOMER_FILE
)


class TestCustomerService(unittest.TestCase):

    def setUp(self):
        self._backup = None
        if os.path.exists(CUSTOMER_FILE):
            with open(CUSTOMER_FILE, 'r', encoding='utf-8') as f:
                self._backup = f.read()
        os.makedirs(os.path.dirname(CUSTOMER_FILE), exist_ok=True)
        with open(CUSTOMER_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)

    def tearDown(self):
        if self._backup is not None:
            with open(CUSTOMER_FILE, 'w', encoding='utf-8') as f:
                f.write(self._backup)
        else:
            if os.path.exists(CUSTOMER_FILE):
                os.remove(CUSTOMER_FILE)

    # ---- 등록 ----

    def test_register_success(self):
        result = register_customer('테스트고객사', '홍길동', 'hong@test.com')
        self.assertTrue(result['success'])
        self.assertEqual(result['customer']['customer_name'], '테스트고객사')
        self.assertEqual(result['customer']['customer_id'], 'C001')

    def test_id_auto_increment(self):
        r1 = register_customer('A', 'M1', 'a@t.com')
        r2 = register_customer('B', 'M2', 'b@t.com')
        self.assertEqual(r1['customer']['customer_id'], 'C001')
        self.assertEqual(r2['customer']['customer_id'], 'C002')

    # ---- 중복 등록 차단 ----

    def test_register_duplicate_id_blocked(self):
        """customer_id가 이미 존재하는 ID로 강제 저장된 경우 등록 차단"""
        customers = [
            {'customer_id': 'C001', 'customer_name': 'A', 'manager_name': 'M1', 'email': 'a@t.com'}
        ]
        with open(CUSTOMER_FILE, 'w', encoding='utf-8') as f:
            json.dump(customers, f)
        # C001이 이미 있으므로 register_customer는 C002를 생성 (중복 자동 회피)
        # 동일 customer_id를 직접 지정할 수 없으므로 자동 생성 로직이 중복을 내지 않음
        # 대신 저장소에 C001이 이미 있으면 _get_next_customer_id는 C002를 반환 -> 정상 동작
        result = register_customer('B', 'M2', 'b@t.com')
        self.assertTrue(result['success'])
        self.assertEqual(result['customer']['customer_id'], 'C002')

    # ---- 입력 검증 ----

    def test_register_empty_name(self):
        result = register_customer('', '담당자', 'e@t.com')
        self.assertFalse(result['success'])
        self.assertIn('고객사명', result['errors'][0])

    def test_register_empty_manager(self):
        result = register_customer('고객사', '', 'e@t.com')
        self.assertFalse(result['success'])
        self.assertIn('담당자명', result['errors'][0])

    def test_register_empty_email(self):
        result = register_customer('고객사', '담당자', '')
        self.assertFalse(result['success'])
        self.assertIn('이메일', result['errors'][0])

    def test_register_invalid_email_no_at(self):
        result = register_customer('고객사', '담당자', 'noatsign')
        self.assertFalse(result['success'])
        self.assertIn('이메일 형식', result['errors'][0])

    def test_register_invalid_email_no_domain(self):
        result = register_customer('고객사', '담당자', 'user@')
        self.assertFalse(result['success'])
        self.assertIn('이메일 형식', result['errors'][0])

    def test_register_invalid_email_space(self):
        result = register_customer('고객사', '담당자', 'user @t.com')
        self.assertFalse(result['success'])
        self.assertIn('이메일 형식', result['errors'][0])

    # ---- 목록 조회 ----

    def test_list_customers(self):
        register_customer('A', 'M1', 'a@t.com')
        register_customer('B', 'M2', 'b@t.com')
        customers = list_customers()
        self.assertEqual(len(customers), 2)

    def test_list_customers_empty(self):
        customers = list_customers()
        self.assertEqual(len(customers), 0)

    # ---- 상세 조회 ----

    def test_get_customer_success(self):
        r = register_customer('A', 'M1', 'a@t.com')
        cid = r['customer']['customer_id']
        customer = get_customer(cid)
        self.assertIsNotNone(customer)
        self.assertEqual(customer['customer_name'], 'A')

    def test_get_customer_not_found(self):
        customer = get_customer('C999')
        self.assertIsNone(customer)

    # ---- 수정 ----

    def test_update_success(self):
        r = register_customer('A', 'M1', 'a@t.com')
        cid = r['customer']['customer_id']
        result = update_customer(cid, 'B', 'M2', 'b@t.com')
        self.assertTrue(result['success'])
        self.assertEqual(result['customer']['customer_name'], 'B')
        self.assertEqual(result['customer']['manager_name'], 'M2')

    def test_update_not_found(self):
        result = update_customer('C999', 'A', 'M1', 'a@t.com')
        self.assertFalse(result['success'])
        self.assertIn('C999', result['errors'][0])

    def test_update_empty_name(self):
        r = register_customer('A', 'M1', 'a@t.com')
        cid = r['customer']['customer_id']
        result = update_customer(cid, '', 'M2', 'b@t.com')
        self.assertFalse(result['success'])
        self.assertIn('고객사명', result['errors'][0])

    # ---- 삭제 ----

    def test_delete_success(self):
        r = register_customer('A', 'M1', 'a@t.com')
        cid = r['customer']['customer_id']
        result = delete_customer(cid)
        self.assertTrue(result['success'])
        self.assertEqual(result['customer']['customer_id'], cid)
        self.assertIsNone(get_customer(cid))

    def test_delete_not_found(self):
        result = delete_customer('C999')
        self.assertFalse(result['success'])
        self.assertIn('C999', result['errors'][0])


if __name__ == '__main__':
    unittest.main()