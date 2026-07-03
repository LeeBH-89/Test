import os
from storage import load_json, save_json


CUSTOMER_FILE = os.path.join('data', 'customers.json')
REPORT_FILE = os.path.join('data', 'sales_reports.json')


def print_header(title):
    print()
    print(f'=== {title} ===')


def main_menu():
    while True:
        print_header('Smart Sales CLI')
        print('   1. 고객사 관리')
        print('   2. 영업일지 관리')
        print('   0. 종료')
        choice = input('   선택: ').strip()

        if choice == '1':
            print_header('고객사 관리')
            print('   (기능 미구현)')
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