import math

# [설정 영역]
BEST_OF_N = 3           # N판
TARGET_SCORE = (BEST_OF_N // 2) + 1  # M선승제
WIN_RATE_SET = 56.0 # A팀의 세트 승률 (매 판 일정하다고 가정, 0~100%)
HANDICAP_VALUE = 1.5 #  핸디캡 값 

def calculate_series_win_rate(p, target_score):
    """
    동적 계획법으로 시리즈 승률 계산
    
    Parameters:
        p: A팀의 세트 승률 (0~1)
        target_score: 승리하기 위해 필요한 세트 수
    
    Returns:
        시리즈 승률 (0~1)
    """
    # DP 테이블 초기화
    dp = [[0.0] * (target_score + 1) for _ in range(target_score + 1)]
    
    # 초기 조건: A가 target_score를 달성하면 승리 확률 = 1
    # B가 target_score를 달성하면 승리 확률 = 0
    # 초기화 0으로 이미 반영됨
    for b in range(target_score):
        dp[target_score][b] = 1.0
    
    # 역순으로 확률 계산
    for a in range(target_score - 1, -1, -1):
        for b in range(target_score - 1, -1, -1):
            dp[a][b] = p * dp[a+1][b] + (1-p) * dp[a][b+1]
    
    return dp[0][0]


def calculate_score_probabilities(p, target_score):
    """
    각 최종 스코어가 나올 확률 계산
    
    Parameters:
        p: A팀의 세트 승률 (0~1)
        target_score: 승리하기 위해 필요한 세트 수
    
    Returns:
        스코어별 확률 {'a:b': probability}
    """
    # 도달 확률 테이블
    reach = [[0.0] * (target_score + 1) for _ in range(target_score + 1)]
    reach[0][0] = 1.0
    
    # 모든 상태의 도달 확률 계산
    for a in range(target_score + 1):
        for b in range(target_score + 1):
            if a == target_score or b == target_score:
                continue
            
            # 도달할 확률이 있는 상태에서만 다음 상태로 확률 분배
            if reach[a][b] > 0:
                reach[a + 1][b] += reach[a][b] * p
                reach[a][b + 1] += reach[a][b] * (1 - p)
    
    # 최종 스코어별 확률 수집
    score_probs = {}
    
    # A팀 승리 스코어
    for b in range(target_score):
        score_probs[f"{target_score}:{b}"] = reach[target_score][b]
    
    # B팀 승리 스코어
    for a in range(target_score):
        score_probs[f"{a}:{target_score}"] = reach[a][target_score]
    
    return score_probs


def calculate_total_games_probabilities(p, target_score):
    """
    총 경기 수별 확률 계산
    
    Parameters:
        p: A팀의 세트 승률 (0~1)
        target_score: 승리하기 위해 필요한 세트 수
    
    Returns:
        총 경기 수별 확률 {total_games: probability}
    """
    score_probs = calculate_score_probabilities(p, target_score)
    total_games_probs = {}
    
    for score, prob in score_probs.items():
        a, b = map(int, score.split(':'))
        total_games = a + b
        total_games_probs[total_games] = total_games_probs.get(total_games, 0) + prob
    
    return total_games_probs

def calculate_handicap_formula(p, target_score, handicap_value):
    """
    핸디캡을 적용한 시리즈 승률 계산
    
    Parameters:
        p: A팀의 세트 승률 (0~1)
        target_score: 승리하기 위해 필요한 세트 수
        handicap_value: 핸디캡 값
    
    Returns:
        핸디캡을 적용한 시리즈 승률 (0~1)
    """
    total_prob = 0.0
    
    # 1. A팀이 M승 k패로 이기는 경우
    for k in range(target_score):  # k는 상대방(B)의 승수 (0 ~ m-1)
        if target_score + handicap_value > k:  # 핸디캡 조건
            # 공식: C(m+k-1, m-1) * p^m * (1-p)^k
            prob = math.comb(target_score + k - 1, target_score - 1) * (p ** target_score) * ((1 - p) ** k)
            total_prob += prob
            
    # 2. B팀이 M승 k패로 이기는 경우 (A는 k승 M패)
    for k in range(target_score):  # k는 A의 승수 (0 ~ m-1)
        if k + handicap_value > target_score:  # 핸디캡 조건
            # 공식: C(m+k-1, m-1) * p^k * (1-p)^m
            prob = math.comb(target_score + k - 1, target_score - 1) * (p ** k) * ((1 - p) ** target_score)
            total_prob += prob
            
    return total_prob


# ==========================================
# 메인 실행 로직
# ==========================================
if __name__ == "__main__":
    p = WIN_RATE_SET / 100
    target_score = TARGET_SCORE
    handicap_value = HANDICAP_VALUE
    
    # 계산 실행
    a_win_prob = calculate_series_win_rate(p, target_score)
    b_win_prob = 1 - a_win_prob
    score_probs = calculate_score_probabilities(p, target_score)
    total_games_probs = calculate_total_games_probabilities(p, target_score)
    
    # ==========================================
    # 결과 출력
    # ==========================================
    print(f"\n{'='*45}")
    print(f"분석 결과: {BEST_OF_N}판 {target_score}선승제 (세트 승률 {p*100:.1f}%)")
    print(f"{'='*45}")
    
    print("\n[1] 최종 시리즈 승률")
    print(f"  A팀 승리 확률: {a_win_prob*100:.2f}%")
    print(f"  B팀 승리 확률: {b_win_prob*100:.2f}%")
    
    print("\n[2] 가장 가능성 높은 스코어")
    sorted_scores = sorted(score_probs.items(), key=lambda x: x[1], reverse=True)
    for i, (score, score_prob) in enumerate(sorted_scores):
        a_score, b_score = map(int, score.split(':'))
        winner = "A승" if a_score > b_score else "B승"
        print(f"  {i+1}위: {score} ({winner}) → {score_prob*100:.2f}%")
    
    print("\n[3] 경기 길이 예상 (Total Games)")
    sorted_games = sorted(total_games_probs.items())
    expected_value = 0
    for games, game_duration_prob in sorted_games:
        print(f"  - {games}세트에서 종료: {game_duration_prob*100:.2f}%")
        expected_value += games * game_duration_prob
    print(f"  → 기대 경기 수: {expected_value:.2f}세트")
    
    result_prob = calculate_handicap_formula(p, target_score, handicap_value)

    print(f"\n[4] 핸디캡({handicap_value}) 적용 후 A팀 승리 확률: {result_prob * 100:.2f}%")
    
    print(f"{'='*45}\n")