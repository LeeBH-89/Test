from modules.customer import (
    register_customer, list_customers, get_customer,
    search_customers, update_customer, delete_customer
)
from modules.csv_export import export_customers_to_csv
from modules.report import (
    register_report, list_reports, get_report, update_report,
    submit_report, approve_report, reject_report, withdraw_report
)


def print_header(title):
    print()
    print(f'=== {title} ===')


def print_result(result):
    if result.get('success'):
        print('✅ 처리 완료')
        for key, value in result.items():
            if key != 'success':
                print(f'   {key}: {value}')
    else:
        print('❌ 오류 발생')
        for err in result.get('errors', []):
            print(f'   - {err}')


def print_customer_table(customers):
    if not customers:
        print('   등록된 고객사가 없습니다.')
        return
    print(f'   총 {len(customers)}건')
    print(f'   {"ID":<8} {"고객사명":<16} {"담당자":<10} {"이메일":<24}')
    print(f'   {"-"*58}')
    for c in customers:
        print(f'   {c["customer_id"]:<8} {c["customer_name"]:<16} {c["manager_name"]:<10} {c["email"]:<24}')


def print_report_table(reports):
    if not reports:
        print('   등록된 영업일지가 없습니다.')
        return
    print(f'   총 {len(reports)}건')
    print(f'   {"ID":<8} {"고객사":<8} {"일자":<14} {"내용":<20} {"상태":<12}')
    print(f'   {"-"*62}')
    for r in reports:
        content = r['content'][:18] + '..' if len(r['content']) > 18 else r['content']
        print(f'   {r["report_id"]:<8} {r["customer_id"]:<8} {r["activity_date"]:<14} {content:<20} {r["status"]:<12}')


def customer_menu():
    while True:
        print_header('고객사 관리')
        print('   1. 등록  2. 목록  3. 상세  4. 검색  5. 수정  6. 삭제  7. CSV 내보내기  0. 뒤로')
        choice = input('   선택: ').strip()

        if choice == '1':
            print_header('고객사 등록')
            name = input('   고객사명: ').strip()
            manager = input('   담당자명: ').strip()
            email = input('   이메일: ').strip()
            result = register_customer(name, manager, email)
            print_result(result)

        elif choice == '2':
            print_header('고객사 목록')
            customers = list_customers()
            print_customer_table(customers)

        elif choice == '3':
            print_header('고객사 상세 조회')
            cid = input('   고객사 ID: ').strip()
            customer = get_customer(cid)
            if customer:
                print(f'   ID: {customer["customer_id"]}')
                print(f'   고객사명: {customer["customer_name"]}')
                print(f'   담당자: {customer["manager_name"]}')
                print(f'   이메일: {customer["email"]}')
            else:
                print(f'   고객사 ID {cid}를 찾을 수 없습니다.')

        elif choice == '4':
            print_header('고객사 검색')
            keyword = input('   검색어: ').strip()
            customers = search_customers(keyword)
            print_customer_table(customers)

        elif choice == '5':
            print_header('고객사 수정')
            cid = input('   고객사 ID: ').strip()
            name = input('   새 고객사명: ').strip()
            manager = input('   새 담당자명: ').strip()
            email = input('   새 이메일: ').strip()
            result = update_customer(cid, name, manager, email)
            print_result(result)

        elif choice == '6':
            print_header('고객사 삭제')
            cid = input('   고객사 ID: ').strip()
            confirm = input(f'   정말 삭제하시겠습니까? (y/n): ').strip().lower()
            if confirm == 'y':
                result = delete_customer(cid)
                print_result(result)
            else:
                print('   삭제가 취소되었습니다.')

        elif choice == '7':
            print_header('고객사 CSV 내보내기')
            result = export_customers_to_csv()
            print_result(result)

        elif choice == '0':
            break

        else:
            print('   잘못된 선택입니다.')


def report_menu():
    while True:
        print_header('영업일지 관리')
        print('   1. 등록  2. 목록  3. 상세  4. 수정')
        print('   5. 상신  6. 승인  7. 반려  8. 회수  0. 뒤로')
        choice = input('   선택: ').strip()

        if choice == '1':
            print_header('영업일지 등록')
            cid = input('   고객사 ID: ').strip()
            date = input('   활동일자 (YYYY-MM-DD): ').strip()
            content = input('   활동내용: ').strip()
            result = register_report(cid, date, content)
            print_result(result)

        elif choice == '2':
            print_header('영업일지 목록')
            reports = list_reports()
            print_report_table(reports)

        elif choice == '3':
            print_header('영업일지 상세 조회')
            rid = input('   영업일지 ID: ').strip()
            report = get_report(rid)
            if report:
                print(f'   ID: {report["report_id"]}')
                print(f'   고객사 ID: {report["customer_id"]}')
                print(f'   활동일자: {report["activity_date"]}')
                print(f'   활동내용: {report["content"]}')
                print(f'   상태: {report["status"]}')
            else:
                print(f'   영업일지 ID {rid}를 찾을 수 없습니다.')

        elif choice == '4':
            print_header('영업일지 수정')
            rid = input('   영업일지 ID: ').strip()
            date = input('   새 활동일자 (YYYY-MM-DD): ').strip()
            content = input('   새 활동내용: ').strip()
            result = update_report(rid, date, content)
            print_result(result)

        elif choice == '5':
            print_header('영업일지 상신')
            rid = input('   영업일지 ID: ').strip()
            result = submit_report(rid)
            print_result(result)

        elif choice == '6':
            print_header('영업일지 승인')
            rid = input('   영업일지 ID: ').strip()
            result = approve_report(rid)
            print_result(result)

        elif choice == '7':
            print_header('영업일지 반려')
            rid = input('   영업일지 ID: ').strip()
            result = reject_report(rid)
            print_result(result)

        elif choice == '8':
            print_header('영업일지 회수')
            rid = input('   영업일지 ID: ').strip()
            result = withdraw_report(rid)
            print_result(result)

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
            report_menu()
        elif choice == '0':
            print('   프로그램을 종료합니다.')
            break
        else:
            print('   잘못된 선택입니다.')


if __name__ == '__main__':
    main_menu()