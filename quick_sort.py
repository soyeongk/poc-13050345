"""
Quick Sort PoC — 알고리즘을 모른다고 가정하고 처음부터 이해하기 위한 예제.

핵심 아이디어:
1. 리스트에서 기준값(pivot)을 하나 고른다.
2. pivot보다 작은 값들 / 큰 값들로 리스트를 둘로 나눈다 (partition).
3. 나뉜 두 리스트를 각각 재귀적으로 quick_sort 한다.
4. (작은 값들 정렬) + pivot + (큰 값들 정렬) 을 합치면 전체가 정렬된다.

시간복잡도: 평균 O(n log n), 최악(이미 정렬된 리스트 + 항상 첫/마지막 원소를 pivot으로 고르는 경우) O(n^2)
"""


def quick_sort(items):
    if len(items) <= 1:
        # 원소가 0개 또는 1개면 이미 정렬된 상태 (재귀 종료 조건)
        return items

    pivot = items[0]
    rest = items[1:]

    smaller = [x for x in rest if x <= pivot]
    larger = [x for x in rest if x > pivot]

    print(f"pivot={pivot} | smaller={smaller} | larger={larger}")

    return quick_sort(smaller) + [pivot] + quick_sort(larger)


def quick_sort_verbose(items, depth=0):
    """호출 깊이(depth)를 출력해서 재귀 흐름을 눈으로 볼 수 있게 한 버전."""
    indent = "  " * depth
    print(f"{indent}quick_sort({items})")

    if len(items) <= 1:
        return items

    pivot = items[0]
    rest = items[1:]
    smaller = [x for x in rest if x <= pivot]
    larger = [x for x in rest if x > pivot]

    sorted_smaller = quick_sort_verbose(smaller, depth + 1)
    sorted_larger = quick_sort_verbose(larger, depth + 1)

    result = sorted_smaller + [pivot] + sorted_larger
    print(f"{indent}-> {result}")
    return result


if __name__ == "__main__":
    sample = [5, 3, 8, 1, 9, 2]

    print("=== 기본 버전 ===")
    print("입력:", sample)
    print("결과:", quick_sort(sample))

    print("\n=== 재귀 흐름 시각화 버전 ===")
    quick_sort_verbose(sample)

    print("\n=== 검증: 내장 sorted()와 결과 비교 ===")
    assert quick_sort(sample) == sorted(sample)
    print("일치함")
