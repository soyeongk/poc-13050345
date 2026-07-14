"""
JSON 파싱 / 저장 PoC
표준 라이브러리 json 모듈만 사용합니다 (별도 설치 불필요).

핵심 개념 4가지:
1. json.loads(str)  -> 문자열을 파이썬 객체로 파싱
2. json.dumps(obj)  -> 파이썬 객체를 문자열로 변환
3. json.load(file)  -> 파일에서 읽어서 파싱
4. json.dump(obj, file) -> 파이썬 객체를 파일로 저장
"""

import json
from pathlib import Path

DATA_FILE = Path(__file__).parent / "sample.json"


def demo_loads_and_dumps():
    # 1) 문자열 -> 파이썬 객체 (dict, list, str, int, float, bool, None으로 매핑됨)
    raw = '{"name": "Sarah", "age": 29, "is_admin": true, "tags": ["dev", "ml"]}'
    parsed = json.loads(raw)
    print("파싱 결과 타입:", type(parsed))
    print("파싱 결과:", parsed)
    print("parsed['name'] ->", parsed["name"])

    # 2) 파이썬 객체 -> 문자열
    # indent: 들여쓰기(가독성), ensure_ascii=False: 한글 등 비ASCII 문자를 유니코드 이스케이프 없이 출력
    dumped = json.dumps(parsed, indent=2, ensure_ascii=False)
    print("\ndumps 결과:\n", dumped)


def demo_save_and_load_file():
    data = {
        "project": "poc",
        "members": ["Sarah", "Alex"],
        "meta": {"version": 1, "active": True},
    }

    # 파일로 저장
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n{DATA_FILE.name} 저장 완료")

    # 파일에서 읽기
    with DATA_FILE.open("r", encoding="utf-8") as f:
        loaded = json.load(f)
    print("파일에서 읽은 데이터:", loaded)
    assert loaded == data  # 저장 전/후 데이터가 동일한지 확인


def demo_error_handling():
    # 잘못된 JSON 문자열 (trailing comma는 JSON 스펙 위반)
    broken = '{"a": 1, "b": 2,}'
    try:
        json.loads(broken)
    except json.JSONDecodeError as e:
        print(f"\n파싱 실패 (의도된 예시): {e}")


if __name__ == "__main__":
    demo_loads_and_dumps()
    demo_save_and_load_file()
    demo_error_handling()
