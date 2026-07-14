"""
연락처 CRUD 콘솔 애플리케이션
json_parser.py에서 사용한 json.load/dump 패턴을 그대로 재사용합니다.

데이터 스키마:
{"id": 1, "name": "Sarah", "email": "sarah@example.com", "phone": "010-1234-5678"}

저장 파일: contacts.json (없으면 최초 실행 시 자동 생성)
"""

import json
import shutil
from pathlib import Path

CONTACTS_FILE = Path(__file__).parent / "contacts.json"


# ---------- 파일 입출력 ----------

def load_contacts():
    if not CONTACTS_FILE.exists():
        return []
    with CONTACTS_FILE.open("r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            backup_path = CONTACTS_FILE.with_suffix(".json.bak")
            shutil.copy(CONTACTS_FILE, backup_path)
            print(
                f"경고: {CONTACTS_FILE.name} 파일이 손상되어 읽을 수 없습니다 ({e}). "
                f"손상된 파일은 {backup_path.name}으로 백업하고 빈 목록으로 시작합니다."
            )
            return []


def save_contacts(contacts):
    with CONTACTS_FILE.open("w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=2, ensure_ascii=False)


def next_id(contacts):
    if not contacts:
        return 1
    return max(c["id"] for c in contacts) + 1


# ---------- Create ----------

def create_contact(contacts):
    print("\n[새 연락처 추가]")
    name = input("이름: ").strip()
    email = input("이메일: ").strip()
    phone = input("전화번호: ").strip()

    if not name:
        print("이름은 필수 입력 항목입니다. 취소합니다.")
        return

    contact = {
        "id": next_id(contacts),
        "name": name,
        "email": email,
        "phone": phone,
    }
    contacts.append(contact)
    save_contacts(contacts)
    print(f"저장 완료: {contact}")


# ---------- Read ----------

def print_contact(c):
    print(f"  [{c['id']}] {c['name']} | {c['email']} | {c['phone']}")


def list_contacts(contacts):
    print("\n[전체 연락처 목록]")
    if not contacts:
        print("  저장된 연락처가 없습니다.")
        return
    for c in contacts:
        print_contact(c)


def find_by_id(contacts, contact_id):
    return next((c for c in contacts if c["id"] == contact_id), None)


def search_contacts(contacts):
    print("\n[연락처 검색]")
    keyword = input("검색할 이름/이메일/전화번호(일부 입력 가능): ").strip().lower()

    results = [
        c for c in contacts
        if keyword in c["name"].lower()
        or keyword in c["email"].lower()
        or keyword in c["phone"].lower()
    ]

    if not results:
        print("  일치하는 연락처가 없습니다.")
        return
    for c in results:
        print_contact(c)


# ---------- Update ----------

def update_contact(contacts):
    print("\n[연락처 수정]")
    contact_id = read_int("수정할 연락처 ID: ")
    if contact_id is None:
        return

    contact = find_by_id(contacts, contact_id)
    if contact is None:
        print(f"  ID {contact_id}에 해당하는 연락처가 없습니다.")
        return

    print_contact(contact)
    print("수정할 필드를 선택하세요 (비워두면 변경하지 않음)")

    for field in ("name", "email", "phone"):
        new_value = input(f"  {field} [{contact[field]}]: ").strip()
        if new_value:
            contact[field] = new_value

    save_contacts(contacts)
    print(f"수정 완료: {contact}")


# ---------- Delete ----------

def delete_contact(contacts):
    print("\n[연락처 삭제]")
    contact_id = read_int("삭제할 연락처 ID: ")
    if contact_id is None:
        return

    contact = find_by_id(contacts, contact_id)
    if contact is None:
        print(f"  ID {contact_id}에 해당하는 연락처가 없습니다.")
        return

    print_contact(contact)
    confirm = input("정말 삭제하시겠습니까? (y/N): ").strip().lower()
    if confirm != "y":
        print("삭제를 취소했습니다.")
        return

    contacts.remove(contact)
    save_contacts(contacts)
    print("삭제 완료")


# ---------- 공통 유틸 ----------

def read_int(prompt):
    raw = input(prompt).strip()
    try:
        return int(raw)
    except ValueError:
        print("  숫자로 된 ID를 입력해주세요.")
        return None


# ---------- 메인 메뉴 ----------

MENU = """
==== 연락처 관리 ====
1. Create - 새 연락처 추가
2. Read   - 전체 목록 보기
3. Search - ID/키워드로 검색
4. Update - 연락처 수정
5. Delete - 연락처 삭제
0. 종료
"""


def main():
    contacts = load_contacts()

    while True:
        print(MENU)
        choice = input("선택: ").strip()

        if choice == "1":
            create_contact(contacts)
        elif choice == "2":
            list_contacts(contacts)
        elif choice == "3":
            search_contacts(contacts)
        elif choice == "4":
            update_contact(contacts)
        elif choice == "5":
            delete_contact(contacts)
        elif choice == "0":
            print("종료합니다.")
            break
        else:
            print("올바른 메뉴 번호를 입력해주세요.")


if __name__ == "__main__":
    main()
