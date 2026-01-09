# [설정 영역]
TARGET_SCORE = 3          # 승리에 필요한 승수 (3판 2선승제면 2)
WIN_RATE = 53.0           # A팀 세트 승률 (%)
CURRENT_SCORE = (1, 1)    # 현재 스코어 (A승수, B승수)

def calculate_series_win_rate(p, target_score, current_a, current_b):
    """
    현재 스코어에서 매치 승리 확률과 다음 세트 승/패 시의 변화를 계산
    
    Parameters:
        p: A팀의 세트 승률 (0~1)
        target_score: 승리하기 위해 필요한 세트 수
        current_a: A팀 현재 승수
        current_b: B팀 현재 승수
    
    Returns:
        현재 매치 승리 확률, 이번 세트를 승리했을 때의 가격, 이번 세트를 패배했을 때의 가격
    """
    # 1. DP 테이블 전체 생성
    dp = [[0.0] * (target_score + 1) for _ in range(target_score + 1)]
    
    # 승패 확정 조건 채우기
    for b in range(target_score):
        dp[target_score][b] = 1.0
    
    # 확률 역산
    for a in range(target_score - 1, -1, -1):
        for b in range(target_score - 1, -1, -1):
            dp[a][b] = p * dp[a+1][b] + (1-p) * dp[a][b+1]
            
    # 2. 필요한 데이터만 추출
    current_price = dp[current_a][current_b]
    
    # 이번 세트 이겼을 때의 가격
    price_if_win = dp[current_a + 1][current_b]
        
    # 이번 세트 졌을 때의 가격
    price_if_loss = dp[current_a][current_b + 1]
        
    return current_price, price_if_win, price_if_loss

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
            if a == target_score or b == target_score:
                continue
            
            if reach[a][b] > 0:
                if a + 1 <= target_score:
                    reach[a + 1][b] += reach[a][b] * p
                if b + 1 <= target_score:
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
        a, b = map(int, score.split(':'))
        total_games = a + b
        remaining = total_games - current_total
        remaining_games_probs[remaining] = remaining_games_probs.get(remaining, 0) + prob
    
    return remaining_games_probs

# --------------------------------------------------------- 


if __name__ == "__main__":

    # 계산
    cur_a, cur_b = CURRENT_SCORE
    p = WIN_RATE / 100
    curr, if_win, if_loss = calculate_series_win_rate(p, TARGET_SCORE, cur_a, cur_b)
    a_win_prob = curr
    b_win_prob = 1 - a_win_prob
    score_probs = calculate_score_probabilities(p, TARGET_SCORE, cur_a, cur_b)
    total_games_probs = calculate_remaining_games_probabilities(score_probs, cur_a, cur_b)
    
    # ==========================================
    # 결과 출력
    # ==========================================
    print(f"{'='*45}\n")
    print(f"분석 결과: {2*TARGET_SCORE-1}판 {TARGET_SCORE}선승제 (세트 승률 {p*100:.1f}%)")
    print(f"현재 스코어: {cur_a}:{cur_b}")

    print("\n[1] 이번 세트에 따른 시리즈 승률")
    print(f"  이번 세트 이기면?     {if_win*100:.2f}%")
    print(f"  이번 세트 지면?       {if_loss*100:.2f}%")
    
    print("\n[2] 최종 시리즈 승률")
    print(f"  A팀 승리 확률: {a_win_prob*100:.2f}%")
    print(f"  B팀 승리 확률: {b_win_prob*100:.2f}%")
    
    print("\n[3] 가장 가능성 높은 스코어")
    sorted_scores = sorted(score_probs.items(), key=lambda x: x[1], reverse=True)
    for i, (score, prob) in enumerate(sorted_scores):
        a_score, b_score = map(int, score.split(':'))
        winner = "A승" if a_score > b_score else "B승"
        print(f"  {i+1}위: {score} ({winner}) → {prob*100:.2f}%")
    
    print("\n[4] 경기 길이 예상 (Total Games)")
    sorted_games = sorted(total_games_probs.items())
    expected_value = 0
    for games, prob in sorted_games:
        total_games = cur_a + cur_b + games
        print(f"  - 총 {total_games}세트에서 종료: {prob*100:.2f}%")
        expected_value += games * prob

    print(f"\n{'='*45}")