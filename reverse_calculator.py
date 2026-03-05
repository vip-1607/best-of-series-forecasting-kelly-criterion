import math
from scipy.optimize import brentq, minimize_scalar

# ===================== [설정 영역] =====================
BEST_OF_N = 3  # N판
TARGET_SCORE = (BEST_OF_N // 2) + 1  # M선승제
CURRENT_SCORE = (0, 0)  # 현재 스코어 (A승수, B승수)

# [역산 입력값]
MARKET_MATCH_PROB = 77  # 시장이 생각하는 매치 승률 (%)
K_LIST = [
    2,
    3,
]  # 남은 경기 길이 리스트 (현재 스코어 기준, 앞으로 몇 세트 더 할 때 끝나는지) #전체 경기로 바꾸고 싶음
PROB_LIST = [53, 42]  # 각 경기 길이에 해당하는 시장 확률 (%)
HANDICAP_VALUE = 1.5  # 핸디캡 값
MARKET_HANDICAP_PROB = 78  # 시장이 생각하는 핸디캡 적용 후 A팀 커버 확률 (%)
# ========================================================


def calculate_series_win_rate(p, target_score, current_a, current_b):
    """
    현재 스코어에서 매치 승률을 계산 (DP 방식)

    Parameters:
        p: A팀의 세트 승률 (0~1)
        target_score: 승리하기 위해 필요한 세트 수
        current_a: A팀 현재 승수
        current_b: B팀 현재 승수

    Returns:
        현재 스코어 기준 A팀의 매치 승률 (0~1)
    """
    dp = [[0.0] * (target_score + 1) for _ in range(target_score + 1)]

    for b in range(target_score):
        dp[target_score][b] = 1.0

    for a in range(target_score - 1, -1, -1):
        for b in range(target_score - 1, -1, -1):
            dp[a][b] = p * dp[a + 1][b] + (1 - p) * dp[a][b + 1]

    return dp[current_a][current_b]


def find_implied_p(market_prob, target_score, current_a=0, current_b=0):
    """
    시장 매치 승률에서 내재된 세트 승률을 브랜트법으로 역산

    Parameters:
        market_prob: 시장에서 거래되는 매치 승률 (0~1)
        target_score: 승리하기 위해 필요한 세트 수
        current_a: A팀 현재 승수 (기본값 0)
        current_b: B팀 현재 승수 (기본값 0)

    Returns:
        내재된 세트 승률 (0~1)
    """

    def objective(p):
        return (
            calculate_series_win_rate(p, target_score, current_a, current_b)
            - market_prob
        )

    return brentq(objective, 0.0001, 0.9999)


def prob_end_at_k(p, k, M, current_a=0, current_b=0):
    """
    현재 스코어에서 앞으로 k세트 더 진행했을 때 시리즈가 끝날 확률

    Parameters:
        p: A팀의 세트 승률 (0~1)
        k: 앞으로 남은 세트 수 (현재 스코어 기준)
        M: 승리하기 위해 필요한 세트 수 (target_score)
        current_a: A팀 현재 승수 (기본값 0)
        current_b: B팀 현재 승수 (기본값 0)

    Returns:
        앞으로 k세트째에서 시리즈가 종료될 확률
    """
    needs_a = M - current_a  # A팀이 앞으로 더 필요한 승수
    needs_b = M - current_b  # B팀이 앞으로 더 필요한 승수
    q = 1 - p

    total = 0.0

    # A가 이기는 경우: needs_a승, (k - needs_a)패
    # 단, 패 수 = k - needs_a < needs_b 이어야 (B가 먼저 끝나지 않음)
    if k >= needs_a and (k - needs_a) < needs_b:
        total += math.comb(k - 1, needs_a - 1) * (p**needs_a) * (q ** (k - needs_a))

    # B가 이기는 경우: needs_b승, (k - needs_b)패
    # 단, 패 수 = k - needs_b < needs_a 이어야 (A가 먼저 끝나지 않음)
    if k >= needs_b and (k - needs_b) < needs_a:
        total += math.comb(k - 1, needs_b - 1) * (q**needs_b) * (p ** (k - needs_b))

    return total


def solve_p_from_prob(game_end_prob, k, M, current_a=0, current_b=0):
    """
    시리즈가 k세트 더 진행 후 끝날 확률이 주어졌을 때, 세트 승률 p를 역산

    Parameters:
        game_end_prob: 경기가 k세트째에서 끝날 확률
        k: 남은 세트 수 (현재 스코어 기준)
        M: 승리하기 위해 필요한 세트 수
        current_a: A팀 현재 승수 (기본값 0)
        current_b: B팀 현재 승수 (기본값 0)

    Returns:
        (p_high, p_low, reason) - 두 구간에서 탐색한 p값과 진단 사유
    """

    def objective(p):
        return prob_end_at_k(p, k, M, current_a, current_b) - game_end_prob

    # 두 구간(0~0.5, 0.5~1)으로 나눠서 각각 탐색
    try:
        p_high = brentq(objective, 0.5, 0.9999)
    except ValueError:
        p_high = None

    try:
        p_low = brentq(
            objective, 0.0001, 0.500001
        )  # p=0.500001로 설정한 이유는 p=0.5일 때 못 찾을수도 있기 때문
    except ValueError:
        p_low = None

    # 진단 사유 판별
    if p_high is not None and p_low is not None:
        reason = None
    elif p_high is not None or p_low is not None:
        if current_a != current_b:
            reason = "비대칭 스코어로 인해 한 구간에서만 해 존재"
        else:
            reason = "시장 확률이 최댓값 근처 (접점)"
    else:
        result = minimize_scalar(
            lambda p: -prob_end_at_k(p, k, M, current_a, current_b),
            bounds=(0.0001, 0.9999),
            method="bounded",
        )
        max_prob = -result.fun
        reason = f"시장 확률({game_end_prob:.4f})이 수학적 최대({max_prob:.4f})를 초과"

    return p_high, p_low, reason


def solve_p_from_multiple_lengths(k_list, prob_list, M, current_a=0, current_b=0):
    """
    여러 경기 길이와 확률이 주어졌을 때, 각 경기 길이에 해당하는 세트 승률 p를 역산

    Parameters:
        k_list: 남은 경기 길이 리스트 (현재 스코어 기준)
        prob_list: 각 경기 길이에 해당하는 확률 리스트
        M: 승리하기 위해 필요한 세트 수
        current_a: A팀 현재 승수 (기본값 0)
        current_b: B팀 현재 승수 (기본값 0)

    Returns:
        각 경기 길이에 해당하는 p값 리스트 [(k, prob, p_high, p_low, reason), ...]
    """
    if len(k_list) != len(prob_list):
        raise ValueError("k_list와 prob_list의 길이가 같아야 합니다.")

    results = []
    for k, game_end_prob in zip(k_list, prob_list):
        p_high, p_low, reason = solve_p_from_prob(
            game_end_prob, k, M, current_a, current_b
        )
        results.append((k, game_end_prob, p_high, p_low, reason))

    return results


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
    needs_a = target_score - current_a
    needs_b = target_score - current_b

    # 1. A팀이 needs_a승 j패 더 해서 이기는 경우
    for j in range(needs_b):
        final_b = current_b + j
        if target_score + handicap_value > final_b:
            prob = (
                math.comb(needs_a + j - 1, needs_a - 1) * (p**needs_a) * ((1 - p) ** j)
            )
            total_prob += prob

    # 2. B팀이 needs_b승 j패 더 해서 이기는 경우 (A는 j승 더 함)
    for j in range(needs_a):
        final_a = current_a + j
        if final_a + handicap_value > target_score:
            prob = (
                math.comb(needs_b + j - 1, needs_b - 1) * (p**j) * ((1 - p) ** needs_b)
            )
            total_prob += prob

    return total_prob


def find_implied_p_handicap(
    market_handicap_prob, target_score, handicap_value, current_a=0, current_b=0
):
    """
    핸디캡 적용 시장 승률에서 내재된 세트 승률을 브랜트법으로 역산

    Parameters:
        market_handicap_prob: 시장에서 거래되는 핸디캡 커버 확률 (0~1)
        target_score: 승리하기 위해 필요한 세트 수
        handicap_value: A팀에게 부여된 핸디캡
        current_a: A팀 현재 승수 (기본값 0)
        current_b: B팀 현재 승수 (기본값 0)

    Returns:
        내재된 세트 승률 (0~1)
    """

    def objective(p):
        return (
            calculate_handicap_formula(
                p, target_score, handicap_value, current_a, current_b
            )
            - market_handicap_prob
        )

    return brentq(objective, 0.0001, 0.9999)


# ===================== [실행] =====================
if __name__ == "__main__":
    cur_a, cur_b = CURRENT_SCORE
    M = TARGET_SCORE
    N = BEST_OF_N

    print("=" * 50)
    print(f"분석 결과: {N}판 {M}선승제")
    print(f"현재 스코어: {cur_a}:{cur_b}")
    print("=" * 50)

    # [1] 매치 승률 → 세트 승률 역산
    print("\n[1] 매치 승률 → 세트 승률 역산")
    implied_p = find_implied_p(MARKET_MATCH_PROB / 100, M, cur_a, cur_b)
    print(f"  시장 매치 승률: {MARKET_MATCH_PROB}%")
    print(f"  → 추정 세트 승률 p: {implied_p*100:.2f}%")
    print(
        f"\n  해석: 현재 스코어 {cur_a}:{cur_b}에서 시장이 매치 승률을 "
        f"{MARKET_MATCH_PROB}%로 평가한다면,"
    )
    print(f"        A팀의 각 세트 승률을 약 {implied_p*100:.2f}%로 보고 있다는 뜻이다.")

    # [2] 경기 길이별 세트 승률 분석
    print("\n[2] 경기 길이별 세트 승률 분석")
    is_a_favorite = MARKET_MATCH_PROB >= 50  # 매치 승률 기준 정배팀 판별
    prob_list_01 = [p / 100 for p in PROB_LIST]  # 함수용 0~1 변환
    results = solve_p_from_multiple_lengths(K_LIST, prob_list_01, M, cur_a, cur_b)
    for k, game_end_prob, p_high, p_low, reason in results:
        total_games = cur_a + cur_b + k
        # 정배팀 승률 선택: A가 정배면 p_high, B가 정배면 p_low
        p_fav = p_high if is_a_favorite else p_low
        print(
            f"  전체 {total_games}세트에서 종료 (남은 {k}세트), 시장 추정 확률={game_end_prob:.4f}"
        )
        if p_fav is not None:
            print(f"    → 정배팀 추정 세트 승률 p: {p_fav:.4f}")
            if reason:
                print(f"    ⚠ {reason}")
        else:
            print(f"    → 매수 주의! 해당 확률을 만족하는 p값이 존재하지 않습니다.")
            print(f"    ⚠ {reason}")

    # [3] 핸디캡 매치 승률 → 세트 승률 역산
    print(f"\n[3] 핸디캡({HANDICAP_VALUE}) 매치 승률 → 세트 승률 역산")
    implied_p_hc = find_implied_p_handicap(
        MARKET_HANDICAP_PROB / 100, M, HANDICAP_VALUE, cur_a, cur_b
    )
    print(f"  시장이 평가한 핸디캡이 적용된 매치 승률: {MARKET_HANDICAP_PROB}%")
    print(f"  → 추정 세트 승률 p: {implied_p_hc*100:.2f}%")
    print(f"\n  해석: 현재 스코어 {cur_a}:{cur_b}에서 핸디캡({HANDICAP_VALUE}) 적용 시")
    print(
        f"        시장이 핸디캡이 적용된 매치 승률을 {MARKET_HANDICAP_PROB}%로 평가한다면,"
    )
    print(
        f"        A팀의 각 세트 승률을 약 {implied_p_hc*100:.2f}%로 보고 있다는 뜻이다."
    )

    print(f"\n{'='*50}")

    # [4] 세트 승률 종합 비교
    all_estimates = []
    all_estimates.append(("매치 승률", implied_p))

    for k, game_end_prob, p_high, p_low, reason in results:
        total_games = cur_a + cur_b + k
        p_fav = p_high if is_a_favorite else p_low
        if p_fav is not None:
            all_estimates.append((f"경기길이({total_games}세트)", p_fav))

    all_estimates.append((f"핸디캡({HANDICAP_VALUE})", implied_p_hc))

    max_source, max_p = max(all_estimates, key=lambda x: x[1])
    min_source, min_p = min(all_estimates, key=lambda x: x[1])

    print(f"\n[4] 세트 승률 종합 비교")
    print(f"  {'종목':<25} {'추정 세트 승률':>12}")
    print(f"  {'-'*25} {'-'*12}")
    for source, p_val in all_estimates:
        marker = (
            " ◀ 최대"
            if (source, p_val) == (max_source, max_p)
            else " ◀ 최소" if (source, p_val) == (min_source, min_p) else ""
        )
        print(f"  {source:<25} {p_val*100:>11.2f}%{marker}")
    print(f"  {'-'*25} {'-'*12}")
    print(f"  {min_source}를 숏치고 {max_source}를 롱잡으세요")

    print(f"\n{'='*50}")
