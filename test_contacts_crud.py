"""
contacts_crud.py에 대한 Regression / Safety 테스트

Regression: 기능이 의도한 대로 계속 동작하는지 (Create/Read/Update/Delete 정상 흐름)
Safety:      위험한 입력(빈 값, 잘못된 타입, 삭제 확인 거부, 손상된 파일 등)에도
             데이터가 훼손되거나 앱이 예기치 않게 죽지 않는지

CONTACTS_FILE을 tmp_path 하위 경로로 monkeypatch해서 실제 contacts.json을
건드리지 않고 격리된 상태로 테스트합니다.
"""

import json

import pytest

import contacts_crud as app


@pytest.fixture(autouse=True)
def isolate_contacts_file(tmp_path, monkeypatch):
    monkeypatch.setattr(app, "CONTACTS_FILE", tmp_path / "contacts.json")


def set_inputs(monkeypatch, values):
    it = iter(values)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(it))


# ---------------------------------------------------------------------------
# Create — Regression
# ---------------------------------------------------------------------------

def test_create_assigns_id_1_when_empty(monkeypatch):
    contacts = []
    set_inputs(monkeypatch, ["Sarah", "sarah@example.com", "010-1111-2222"])

    app.create_contact(contacts)

    assert contacts == [
        {"id": 1, "name": "Sarah", "email": "sarah@example.com", "phone": "010-1111-2222"}
    ]
    assert json.loads(app.CONTACTS_FILE.read_text(encoding="utf-8")) == contacts


def test_create_assigns_next_id_as_max_plus_1(monkeypatch):
    contacts = [{"id": 1, "name": "Sarah", "email": "", "phone": ""},
                {"id": 5, "name": "Alex", "email": "", "phone": ""}]
    set_inputs(monkeypatch, ["Bob", "bob@example.com", "010-0000-0000"])

    app.create_contact(contacts)

    assert contacts[-1]["id"] == 6


# ---------------------------------------------------------------------------
# Create — Safety
# ---------------------------------------------------------------------------

def test_create_rejects_empty_name(monkeypatch):
    contacts = []
    set_inputs(monkeypatch, ["   ", "x@example.com", "010-0000-0000"])

    app.create_contact(contacts)

    assert contacts == []
    assert not app.CONTACTS_FILE.exists()


def test_create_allows_unicode_and_special_characters(monkeypatch):
    contacts = []
    set_inputs(monkeypatch, ["박서연 😀", "a+b@example.com", "010-!@#-0000"])

    app.create_contact(contacts)

    assert contacts[0]["name"] == "박서연 😀"
    reloaded = json.loads(app.CONTACTS_FILE.read_text(encoding="utf-8"))
    assert reloaded[0]["name"] == "박서연 😀"


def test_create_allows_duplicate_names(monkeypatch):
    contacts = [{"id": 1, "name": "Sarah", "email": "a@x.com", "phone": ""}]
    set_inputs(monkeypatch, ["Sarah", "b@x.com", ""])

    app.create_contact(contacts)

    names = [c["name"] for c in contacts]
    assert names.count("Sarah") == 2  # 현재 구현은 중복 이름을 막지 않음 (의도된 동작 문서화)


# ---------------------------------------------------------------------------
# Read — Regression / Safety
# ---------------------------------------------------------------------------

def test_list_contacts_on_empty_list_does_not_crash(capsys):
    app.list_contacts([])
    out = capsys.readouterr().out
    assert "저장된 연락처가 없습니다" in out


def test_search_is_case_insensitive(monkeypatch, capsys):
    contacts = [{"id": 1, "name": "Sarah", "email": "sarah@example.com", "phone": "010-1111-2222"}]
    set_inputs(monkeypatch, ["SARAH"])

    app.search_contacts(contacts)

    out = capsys.readouterr().out
    assert "Sarah" in out


def test_search_no_match_does_not_crash(monkeypatch, capsys):
    contacts = [{"id": 1, "name": "Sarah", "email": "", "phone": ""}]
    set_inputs(monkeypatch, ["nonexistent"])

    app.search_contacts(contacts)

    out = capsys.readouterr().out
    assert "일치하는 연락처가 없습니다" in out


def test_find_by_id_missing_returns_none():
    contacts = [{"id": 1, "name": "Sarah", "email": "", "phone": ""}]
    assert app.find_by_id(contacts, 999) is None


# ---------------------------------------------------------------------------
# Update — Regression / Safety
# ---------------------------------------------------------------------------

def test_update_changes_only_provided_fields(monkeypatch):
    contacts = [{"id": 1, "name": "Sarah", "email": "old@example.com", "phone": "010-1111-2222"}]
    set_inputs(monkeypatch, ["1", "", "new@example.com", ""])  # id, name(유지), email(변경), phone(유지)

    app.update_contact(contacts)

    assert contacts[0] == {
        "id": 1, "name": "Sarah", "email": "new@example.com", "phone": "010-1111-2222"
    }


def test_update_nonexistent_id_does_not_crash(monkeypatch, capsys):
    contacts = [{"id": 1, "name": "Sarah", "email": "", "phone": ""}]
    set_inputs(monkeypatch, ["999"])

    app.update_contact(contacts)

    out = capsys.readouterr().out
    assert "해당하는 연락처가 없습니다" in out
    assert contacts == [{"id": 1, "name": "Sarah", "email": "", "phone": ""}]  # 변경 없음


def test_update_with_non_numeric_id_does_not_crash(monkeypatch, capsys):
    contacts = [{"id": 1, "name": "Sarah", "email": "", "phone": ""}]
    set_inputs(monkeypatch, ["abc"])

    app.update_contact(contacts)

    out = capsys.readouterr().out
    assert "숫자로 된 ID를 입력해주세요" in out
    assert contacts == [{"id": 1, "name": "Sarah", "email": "", "phone": ""}]  # 변경 없음


def test_update_cannot_modify_id(monkeypatch):
    # update 메뉴는 name/email/phone만 입력받고 id는 애초에 입력 항목이 아니므로
    # id가 절대 바뀌지 않는지 회귀 확인
    contacts = [{"id": 1, "name": "Sarah", "email": "", "phone": ""}]
    set_inputs(monkeypatch, ["1", "SarahNew", "", ""])

    app.update_contact(contacts)

    assert contacts[0]["id"] == 1


# ---------------------------------------------------------------------------
# Delete — Safety (핵심: 실수로 삭제되지 않아야 함)
# ---------------------------------------------------------------------------

def test_delete_confirmed_removes_contact(monkeypatch):
    contacts = [{"id": 1, "name": "Sarah", "email": "", "phone": ""}]
    set_inputs(monkeypatch, ["1", "y"])

    app.delete_contact(contacts)

    assert contacts == []


def test_delete_declined_keeps_contact(monkeypatch):
    contacts = [{"id": 1, "name": "Sarah", "email": "", "phone": ""}]
    set_inputs(monkeypatch, ["1", "n"])

    app.delete_contact(contacts)

    assert len(contacts) == 1


def test_delete_confirmation_requires_exact_y(monkeypatch):
    # 'yes', 엔터(빈 입력) 등 'y'가 아닌 모든 입력은 삭제를 취소해야 함 (안전한 기본값)
    contacts = [{"id": 1, "name": "Sarah", "email": "", "phone": ""}]
    set_inputs(monkeypatch, ["1", "yes"])

    app.delete_contact(contacts)

    assert len(contacts) == 1  # 'yes'는 'y'와 다르므로 삭제되면 안 됨


def test_delete_accepts_uppercase_y(monkeypatch):
    contacts = [{"id": 1, "name": "Sarah", "email": "", "phone": ""}]
    set_inputs(monkeypatch, ["1", "Y"])

    app.delete_contact(contacts)

    assert contacts == []


def test_delete_nonexistent_id_does_not_crash(monkeypatch, capsys):
    contacts = [{"id": 1, "name": "Sarah", "email": "", "phone": ""}]
    set_inputs(monkeypatch, ["999"])

    app.delete_contact(contacts)

    out = capsys.readouterr().out
    assert "해당하는 연락처가 없습니다" in out
    assert len(contacts) == 1


# ---------------------------------------------------------------------------
# 파일 I/O — Regression / Safety
# ---------------------------------------------------------------------------

def test_load_contacts_missing_file_returns_empty_list():
    assert app.load_contacts() == []


def test_save_then_load_round_trip():
    contacts = [{"id": 1, "name": "Sarah", "email": "s@example.com", "phone": "010-0000-0000"}]
    app.save_contacts(contacts)

    assert app.load_contacts() == contacts


def test_load_contacts_with_corrupted_json_falls_back_to_empty_list(capsys):
    app.CONTACTS_FILE.write_text('{"broken": ', encoding="utf-8")

    result = app.load_contacts()

    assert result == []
    out = capsys.readouterr().out
    assert "손상되어 읽을 수 없습니다" in out


def test_load_contacts_with_corrupted_json_backs_up_original_file():
    app.CONTACTS_FILE.write_text('{"broken": ', encoding="utf-8")

    app.load_contacts()

    backup_path = app.CONTACTS_FILE.with_suffix(".json.bak")
    assert backup_path.exists()
    assert backup_path.read_text(encoding="utf-8") == '{"broken": '
