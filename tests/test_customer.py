import unittest
import os
import json
from modules.customer import (
    register_customer, list_customers, get_customer,
    search_customers, update_customer, delete_customer,
    CUSTOMER_FILE
)


class TestCustomer(unittest.TestCase):

    def setUp(self):
        self._backup = None
        if os.path.exists(CUSTOMER_FILE):
            with open(CUSTOMER_FILE, 'r', encoding='utf-8') as f:
                self._backup = f.read()
        # 빈 데이터로 초기화
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

    # 1. 등록 정상 동작
    def test_register_success(self):
        result = register_customer('테스트고객사', '홍길동', 'hong@test.com')
        self.assertTrue(result['success'])
        self.assertEqual(result['customer']['customer_name'], '테스트고객사')
        self.assertEqual(result['customer']['customer_id'], 'C001')

    # 2. ID 자동 증가
    def test_id_auto_increment(self):
        r1 = register_customer('A', 'M1', 'a@t.com')
        r2 = register_customer('B', 'M2', 'b@t.com')
        self.assertEqual(r1['customer']['customer_id'], 'C001')
        self.assertEqual(r2['customer']['customer_id'], 'C002')

    # 3. 공백 입력 차단
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

    # 4. 이메일 형식 검증
    def test_register_invalid_email(self):
        result = register_customer('고객사', '담당자', 'noatsign')
        self.assertFalse(result['success'])
        self.assertIn('@', result['errors'][0])

    # 5. 전체 목록 조회
    def test_list_customers(self):
        register_customer('A', 'M1', 'a@t.com')
        register_customer('B', 'M2', 'b@t.com')
        customers = list_customers()
        self.assertEqual(len(customers), 2)

    # 6. 상세 조회 (존재/부재)
    def test_get_customer_success(self):
        r = register_customer('A', 'M1', 'a@t.com')
        cid = r['customer']['customer_id']
        customer = get_customer(cid)
        self.assertIsNotNone(customer)
        self.assertEqual(customer['customer_name'], 'A')

    def test_get_customer_not_found(self):
        customer = get_customer('C999')
        self.assertIsNone(customer)

    # 7. 검색 (부분 일치/불일치)
    def test_search_by_name(self):
        register_customer('삼성전자', '김삼성', 'ss@t.com')
        register_customer('LG전자', '이엘지', 'lg@t.com')
        result = search_customers('삼성')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['customer_name'], '삼성전자')

    def test_search_by_manager(self):
        register_customer('A', '홍길동', 'a@t.com')
        result = search_customers('홍길동')
        self.assertEqual(len(result), 1)

    def test_search_no_match(self):
        result = search_customers('존재하지않음')
        self.assertEqual(len(result), 0)

    def test_search_empty_keyword(self):
        result = search_customers('')
        self.assertEqual(len(result), 0)

    # 8. 수정 정상 동작
    def test_update_success(self):
        r = register_customer('A', 'M1', 'a@t.com')
        cid = r['customer']['customer_id']
        result = update_customer(cid, 'B', 'M2', 'b@t.com')
        self.assertTrue(result['success'])
        self.assertEqual(result['customer']['customer_name'], 'B')
        self.assertEqual(result['customer']['manager_name'], 'M2')

    # 9. 존재하지 않는 ID 수정/삭제 차단
    def test_update_not_found(self):
        result = update_customer('C999', 'A', 'M1', 'a@t.com')
        self.assertFalse(result['success'])
        self.assertIn('C999', result['errors'][0])

    def test_delete_not_found(self):
        result = delete_customer('C999')
        self.assertFalse(result['success'])
        self.assertIn('C999', result['errors'][0])

    # 10. 삭제 정상 동작
    def test_delete_success(self):
        r = register_customer('A', 'M1', 'a@t.com')
        cid = r['customer']['customer_id']
        result = delete_customer(cid)
        self.assertTrue(result['success'])
        self.assertEqual(result['customer']['customer_id'], cid)
        self.assertIsNone(get_customer(cid))


if __name__ == '__main__':
    unittest.main()