# poc-13050345

낯선 코드를 직접 PoC로 실행해보며 이해하기 위한 학습용 저장소입니다.

- `json_parser.py` — 표준 라이브러리 `json`으로 파싱/저장/에러 핸들링 데모
- `quick_sort.py` — Quick Sort 알고리즘을 재귀 흐름 시각화와 함께 학습
- `contacts_crud.py` — JSON 파일(`contacts.json`)로 연락처를 관리하는 CRUD 콘솔 앱
- `test_contacts_crud.py` — `contacts_crud.py`에 대한 pytest 회귀/안전성 테스트

## 1. 준비 (최초 1회)

Python 3.14 기준입니다. 저장소를 clone한 뒤 가상환경을 만들고 활성화합니다.

```powershell
git clone https://github.com/soyeongk/poc-13050345.git
cd poc-13050345

python -m venv .venv
.venv\Scripts\activate
```

테스트를 실행하려면 pytest를 설치합니다 (예제 스크립트만 실행할 경우 불필요).

```powershell
pip install pytest
```

## 2. JSON 파싱/저장 예제 실행

```powershell
python json_parser.py
```

`json.loads/dumps`(문자열 변환)와 `json.load/dump`(파일 입출력) 결과, 그리고 잘못된 JSON을 파싱할 때 발생하는 에러 예시가 출력됩니다. 실행하면 `sample.json` 파일이 생성됩니다.

## 3. Quick Sort 예제 실행

```powershell
python quick_sort.py
```

기본 정렬 결과, 재귀 호출 흐름을 들여쓰기로 시각화한 결과, `sorted()`와의 비교 검증이 순서대로 출력됩니다.

## 4. 연락처 CRUD 콘솔 앱 실행

```powershell
python contacts_crud.py
```

메뉴에서 번호를 입력해 기능을 선택합니다.

```
1. Create - 새 연락처 추가
2. Read   - 전체 목록 보기
3. Search - 이름/이메일/전화번호로 검색
4. Update - 연락처 수정 (빈 입력은 기존 값 유지)
5. Delete - 연락처 삭제 (y 입력 시에만 삭제)
0. 종료
```

데이터는 실행 위치의 `contacts.json`에 저장되며, 파일이 없으면 최초 실행 시 자동 생성됩니다. 파일이 손상된 경우 앱이 `contacts.json.bak`으로 백업하고 빈 목록으로 시작합니다.

## 5. 테스트 실행

```powershell
pytest test_contacts_crud.py -v
```

실제 `contacts.json`은 건드리지 않고 임시 파일로 격리해서 테스트합니다.
