# [설정 영역]
TARGET_SCORE = 2          # 승리에 필요한 선취 승수 (3판 2선승제면 2)
WIN_RATE = 53.0           # A팀 세트 승률 (%)
CURRENT_SCORE = (1, 1)    # 현재 스코어 (A승수, B승수)

def get_arbitrage_stats(p, target_score, current_a, current_b):
    """
    현재 스코어에서 매치 승리 확률과 다음 세트 승/패 시의 변화를 계산
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

if __name__ == "__main__":
    cur_a, cur_b = CURRENT_SCORE
    p = WIN_RATE / 100
    
    # 계산
    curr, if_win, if_loss = get_arbitrage_stats(p, TARGET_SCORE, cur_a, cur_b)
    
    print(f"현재 상황: {cur_a}:{cur_b} (세트 승률 {p})")
    print("----------------------------------------")
    print(f"[1] 현재 매치 승리 적정가: {curr:.4f} ({curr*100:.1f}%)")
    print(f"[2] 이번 세트 이기면?     {if_win:.4f}")
    print(f"[3] 이번 세트 지면?       {if_loss:.4f}")