import unittest
import os
import json
from modules.customer import register_customer, CUSTOMER_FILE
from modules.csv_export import export_customers_to_csv, EXPORT_DIR


class TestCsvExport(unittest.TestCase):

    def setUp(self):
        self._cust_backup = None
        if os.path.exists(CUSTOMER_FILE):
            with open(CUSTOMER_FILE, 'r', encoding='utf-8') as f:
                self._cust_backup = f.read()
        os.makedirs(os.path.dirname(CUSTOMER_FILE), exist_ok=True)
        with open(CUSTOMER_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)

        # 테스트 후 생성된 CSV 파일 정리를 위해 보관
        self._generated_csvs = []

    def tearDown(self):
        if self._cust_backup is not None:
            with open(CUSTOMER_FILE, 'w', encoding='utf-8') as f:
                f.write(self._cust_backup)
        else:
            if os.path.exists(CUSTOMER_FILE):
                os.remove(CUSTOMER_FILE)

        # 생성된 CSV 파일 정리
        for csv_path in self._generated_csvs:
            if os.path.exists(csv_path):
                os.remove(csv_path)

    # 1. CSV 내보내기 정상 동작
    def test_export_success(self):
        register_customer('삼성전자', '김삼성', 'ss@test.com')
        register_customer('LG전자', '이엘지', 'lg@test.com')

        result = export_customers_to_csv()
        self.assertTrue(result['success'])
        self.assertEqual(result['count'], 2)
        self.assertTrue(result['filepath'].endswith('.csv'))
        self._generated_csvs.append(result['filepath'])

        # CSV 파일 내용 확인
        with open(result['filepath'], 'r', encoding='utf-8-sig') as f:
            content = f.read()
        self.assertIn('customer_id', content)
        self.assertIn('삼성전자', content)
        self.assertIn('C001', content)
        self.assertIn('C002', content)

    # 2. 데이터가 없을 때 오류 반환
    def test_export_empty(self):
        result = export_customers_to_csv()
        self.assertFalse(result['success'])
        self.assertIn('내보낼 고객사 데이터가 없습니다.', result['errors'][0])

    # 3. CSV 파일이 exports 폴더에 생성되는지 확인
    def test_export_location(self):
        register_customer('A', 'M', 'a@t.com')
        result = export_customers_to_csv()
        self.assertTrue(result['success'])
        self._generated_csvs.append(result['filepath'])
        # exports 폴더 안에 파일이 생성되었는지 확인
        self.assertTrue(result['filepath'].startswith(EXPORT_DIR))


if __name__ == '__main__':
    unittest.main()