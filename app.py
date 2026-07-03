import os
from storage import load_json, save_json
from customer_service import (
    register_customer, list_customers, get_customer,
    update_customer, delete_customer, search_customers
)


CUSTOMER_FILE = os.path.join('data', 'customers.json')
REPORT_FILE = os.path.join('data', 'sales_reports.json')


def print_header(title):
    print()
    print(f'=== {title} ===')


def customer_menu():
    while True:
        print_header('고객사 관리')
        print('   1. 등록')
        print('   2. 목록')
        print('   3. 상세 조회')
        print('   4. 수정')
        print('   5. 삭제')
        print('   6. 검색')
        print('   0. 뒤로 가기')
        choice = input('   선택: ').strip()

        if choice == '1':
            print_header('고객사 등록')
            name = input('   고객사명: ').strip()
            manager = input('   담당자명: ').strip()
            email = input('   이메일: ').strip()
            result = register_customer(name, manager, email)
            if result['success']:
                c = result['customer']
                print(f'   등록 완료: {c["customer_id"]} - {c["customer_name"]}')
            else:
                for err in result['errors']:
                    print(f'   오류: {err}')

        elif choice == '2':
            print_header('고객사 목록')
            customers = list_customers()
            if not customers:
                print('   등록된 고객사가 없습니다.')
            else:
                for c in customers:
                    print(f'   {c["customer_id"]} | {c["customer_name"]} | {c["manager_name"]} | {c["email"]}')

        elif choice == '3':
            print_header('고객사 상세 조회')
            cid = input('   고객사 ID: ').strip()
            c = get_customer(cid)
            if c:
                print(f'   ID: {c["customer_id"]}')
                print(f'   고객사명: {c["customer_name"]}')
                print(f'   담당자명: {c["manager_name"]}')
                print(f'   이메일: {c["email"]}')
            else:
                print(f'   고객사 ID {cid}를 찾을 수 없습니다.')

        elif choice == '4':
            print_header('고객사 수정')
            cid = input('   고객사 ID: ').strip()
            name = input('   새 고객사명: ').strip()
            manager = input('   새 담당자명: ').strip()
            email = input('   새 이메일: ').strip()
            result = update_customer(cid, name, manager, email)
            if result['success']:
                print(f'   수정 완료: {cid}')
            else:
                for err in result['errors']:
                    print(f'   오류: {err}')

        elif choice == '5':
            print_header('고객사 삭제')
            cid = input('   고객사 ID: ').strip()
            result = delete_customer(cid)
            if result['success']:
                print(f'   삭제 완료: {cid}')
            else:
                for err in result['errors']:
                    print(f'   오류: {err}')

        elif choice == '6':
            print_header('고객사 검색')
            keyword = input('   검색어: ').strip()
            results = search_customers(keyword)
            if not results:
                print('   검색 결과가 없습니다.')
            else:
                for c in results:
                    print(f'   {c["customer_id"]} | {c["customer_name"]} | {c["manager_name"]} | {c["email"]}')

        elif choice == '0':
            break
        else:
            print('   잘못된 선택입니다.')


def main_menu():
    while True:
        print_header('Smart Sales CLI')
        print('   1. 고객사 관리')
        print('   2. 영업일지 관리')
        print('   0. 종료')
        choice = input('   선택: ').strip()

        if choice == '1':
            customer_menu()
        elif choice == '2':
            print_header('영업일지 관리')
            print('   (기능 미구현)')
        elif choice == '0':
            print('   프로그램을 종료합니다.')
            break
        else:
            print('   잘못된 선택입니다.')


if __name__ == '__main__':
    main_menu()
