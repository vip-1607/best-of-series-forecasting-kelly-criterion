import math

# [설정 영역]
BEST_OF_N = 5  # N판
TARGET_SCORE = (BEST_OF_N // 2) + 1  # M선승제
WIN_RATE_SET = 53.0  # A팀의 세트 승률 (매 판 일정하다고 가정, 0~100%)
CURRENT_SCORE = (1, 1)  # 현재 스코어 (A승수, B승수)
HANDICAP_VALUE = 1.5  #  핸디캡 값


def calculate_series_win_rate(p, target_score, current_a, current_b):
    """
    현재 스코어에서 매치 승률과 다음 세트 승/패 시의 매치 승률의 변화를 계산

    Parameters:
        p: A팀의 세트 승률 (0~1)
        target_score: 승리하기 위해 필요한 세트 수
        current_a: A팀 현재 승수
        current_b: B팀 현재 승수

    Returns:
        현재 매치 승률, 이번 세트를 승리했을 때의 매치 승률, 이번 세트를 패배했을 때의 매치 승률
    """
    # 1. DP 테이블 전체 생성
    dp = [[0.0] * (target_score + 1) for _ in range(target_score + 1)]

    # 승패 확정 조건 채우기
    for b in range(target_score):
        dp[target_score][b] = 1.0

    # 확률 역산
    for a in range(target_score - 1, -1, -1):
        for b in range(target_score - 1, -1, -1):
            dp[a][b] = p * dp[a + 1][b] + (1 - p) * dp[a][b + 1]

    # 2. 필요한 데이터만 추출
    current_prob = dp[current_a][current_b]

    # 이번 세트 이겼을 때의 매치 승률
    prob_if_win = dp[current_a + 1][current_b]

    # 이번 세트 졌을 때의 매치 승률
    prob_if_loss = dp[current_a][current_b + 1]

    return current_prob, prob_if_win, prob_if_loss


def calculate_score_probabilities(p, target_score, current_a, current_b):
    """
    현재 스코어에서 도달 가능한 최종 스코어별 확률 계산

    Parameters:
        p: A팀의 세트 승률 (0~1)
        target_score: 승리하기 위해 필요한 세트 수
        current_a: A팀 현재 승수
        current_b: B팀 현재 승수

    Returns:
        스코어별 확률 {'a:b': probability}
    """
    # 도달 확률 테이블
    reach = [[0.0] * (target_score + 1) for _ in range(target_score + 1)]
    reach[current_a][current_b] = 1.0

    # 모든 상태의 도달 확률 계산
    for a in range(current_a, target_score + 1):
        for b in range(current_b, target_score + 1):
            # 누군가 이미 목표 점수에 도달한 상태면 더 이상 확률이 퍼져나가지 않음
            if a == target_score or b == target_score:
                continue

            # 도달할 확률이 있는 상태에서만 다음 상태로 확률 분배
            if reach[a][b] > 0:
                reach[a + 1][b] += reach[a][b] * p
                reach[a][b + 1] += reach[a][b] * (1 - p)

    # 최종 스코어별 확률 수집 (도달 가능한 것만)
    score_probs = {}

    # A팀 승리 스코어
    for b in range(current_b, target_score):
        if reach[target_score][b] > 0:
            score_probs[f"{target_score}:{b}"] = reach[target_score][b]

    # B팀 승리 스코어
    for a in range(current_a, target_score):
        if reach[a][target_score] > 0:
            score_probs[f"{a}:{target_score}"] = reach[a][target_score]

    return score_probs


def calculate_remaining_games_probabilities(score_probs, current_a, current_b):
    """
    이미 계산된 score_probs를 받아서 남은 경기 수별 확률 계산

    Parameters:
        score_probs: calculate_score_probabilities()에서 반환된 스코어별 확률
        current_a: A팀 현재 승수
        current_b: B팀 현재 승수

    Returns:
        남은 경기 수별 확률 {remaining_games: probability}
    """
    remaining_games_probs = {}

    current_total = current_a + current_b
    for score, prob in score_probs.items():
        a, b = map(int, score.split(":"))
        total_games = a + b
        remaining = total_games - current_total
        remaining_games_probs[remaining] = (
            remaining_games_probs.get(remaining, 0) + prob
        )

    return remaining_games_probs


def calculate_handicap_formula(
    p, target_score, handicap_value, current_a=0, current_b=0
):
    """
    현재 스코어에서 핸디캡을 적용한 시리즈 승률 계산

    Parameters:
        p: A팀의 세트 승률 (0~1)
        target_score: 승리하기 위해 필요한 세트 수
        handicap_value: A팀에게 부여된 핸디캡 (예: +1.5면 A 세트 수에 1.5 더함)
        current_a: A팀 현재 승수 (기본값 0)
        current_b: B팀 현재 승수 (기본값 0)

    Returns:
        현재 스코어 기준 핸디캡 적용 후 A팀 승리 확률 (0~1)
    """
    total_prob = 0.0
    needs_a = target_score - current_a  # A팀이 앞으로 더 필요한 승수
    needs_b = target_score - current_b  # B팀이 앞으로 더 필요한 승수

    # 1. A팀이 needs_a승 j패 더 해서 이기는 경우
    for j in range(needs_b):  # j: A가 추가로 지는 세트 수 (0 ~ needs_b-1)
        # 최종 총 스코어: A = target_score, B = current_b + j
        final_b = current_b + j
        if target_score + handicap_value > final_b:  # 핸디캡 조건 (총 세트 기준)
            prob = (
                math.comb(needs_a + j - 1, needs_a - 1) * (p**needs_a) * ((1 - p) ** j)
            )
            total_prob += prob

    # 2. B팀이 needs_b승 j패 더 해서 이기는 경우 (A는 j승 더 함)
    for j in range(needs_a):  # j: A가 추가로 이기는 세트 수 (0 ~ needs_a-1)
        # 최종 총 스코어: A = current_a + j, B = target_score
        final_a = current_a + j
        if final_a + handicap_value > target_score:  # 핸디캡 조건 (총 세트 기준)
            prob = (
                math.comb(needs_b + j - 1, needs_b - 1) * (p**j) * ((1 - p) ** needs_b)
            )
            total_prob += prob

    return total_prob


# ---------------------------------------------------------


if __name__ == "__main__":

    # 계산
    cur_a, cur_b = CURRENT_SCORE
    p = WIN_RATE_SET / 100
    a_win_prob, if_win, if_loss = calculate_series_win_rate(
        p, TARGET_SCORE, cur_a, cur_b
    )
    b_win_prob = 1 - a_win_prob
    score_probs = calculate_score_probabilities(p, TARGET_SCORE, cur_a, cur_b)
    total_games_probs = calculate_remaining_games_probabilities(
        score_probs, cur_a, cur_b
    )

    # ==========================================
    # 결과 출력
    # ==========================================
    print(f"{'='*45}\n")
    print(f"분석 결과: {BEST_OF_N}판 {TARGET_SCORE}선승제 (세트 승률 {p*100:.1f}%)")
    print(f"현재 스코어: {cur_a}:{cur_b}")

    print("\n[1] 이번 세트에 따른 시리즈 승률")
    print(f"  이번 세트 승리시     {if_win*100:.2f}%")
    print(f"  이번 세트 패배시     {if_loss*100:.2f}%")

    print("\n[2] 최종 시리즈 승률")
    print(f"  A팀 승리 확률: {a_win_prob*100:.2f}%")
    print(f"  B팀 승리 확률: {b_win_prob*100:.2f}%")

    print("\n[3] 가장 가능성 높은 스코어")
    sorted_scores = sorted(score_probs.items(), key=lambda x: x[1], reverse=True)
    for i, (score, score_prob) in enumerate(sorted_scores):
        a_score, b_score = map(int, score.split(":"))
        winner = "A승" if a_score > b_score else "B승"
        print(f"  {i+1}위: {score} ({winner}) → {score_prob*100:.2f}%")

    print("\n[4] 경기 길이 예상 (Total Games)")
    sorted_games = sorted(total_games_probs.items())
    expected_value = 0
    for games, game_duration_prob in sorted_games:
        total_games = cur_a + cur_b + games
        print(f"  - 총 {total_games}세트에서 종료: {game_duration_prob*100:.2f}%")
        expected_value += games * game_duration_prob
    print(f"  → 기대 총 경기 수:   {cur_a + cur_b + expected_value:.2f}세트")

    result_prob = calculate_handicap_formula(
        p, TARGET_SCORE, HANDICAP_VALUE, cur_a, cur_b
    )
    print(
        f"\n[5] 핸디캡({HANDICAP_VALUE}) 적용 후 A팀 시리즈 승리 확률: {result_prob * 100:.2f}%"
    )

    print(f"\n{'='*45}")
