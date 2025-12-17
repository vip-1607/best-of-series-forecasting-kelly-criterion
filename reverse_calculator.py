import sys
import io

# Windows 인코딩 문제 해결
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ==========================================
# ⚙️ [설정 영역]
# ==========================================
market_price = 0.51  # 시장이 생각하는 매치 승률 (0~1, 예: 0.85 = 85%)
target_score = 2   # 승리하기 위해 필요한 세트 수
# ==========================================


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


def find_implied_p(market_prob, target_score, tolerance=1e-10, max_iterations=50):
    """
    시장 가격에서 내재된 세트 승률 역산
    
    Parameters:
        market_prob: 시장에서 거래되는 확률 (0~1)
        target_score: 승리하기 위해 필요한 세트 수
        tolerance: 수렴 허용 오차
        max_iterations: 최대 반복 횟수
    
    Returns:
        내재된 세트 승률 (0~1)
    """
    low = 0.0
    high = 1.0
    
    for _ in range(max_iterations):
        mid = (low + high) / 2
        calculated_prob = calculate_series_win_rate(mid, target_score)
        
        if abs(calculated_prob - market_prob) < tolerance:
            return mid
        
        if calculated_prob < market_prob:
            low = mid
        else:
            high = mid
    
    return (low + high) / 2


# ==========================================
# 메인 실행 로직
# ==========================================
if __name__ == "__main__":
    # 내재된 세트 승률 계산
    implied_p = find_implied_p(market_price, target_score)
    
    # 결과 출력
    print(f"\n{'='*50}")
    print("📊 [시장 분석]")
    print(f"{'='*50}")
    
    print("\n[시장 정보]")
    print(f"  시장 가격: {market_price*100:.2f}% (최종 시리즈 승률)")
    print(f"  경기 형식: {2*target_score-1}전 {target_score}선승제")
    
    print("\n[계산 결과]")
    print(f"  🎯 시장이 생각하는 세트 승률(p): {implied_p*100:.2f}%")    

    print(f"\n{'='*50}")
    print("\n💡 해석:")
    print(f"   시장에서 {market_price*100:.0f}%로 거래된다는 것은")
    print(f"   A팀의 각 세트 승률을 약 {implied_p*100:.2f}%로 평가한다는 뜻이다.")
    print(f"{'='*50}\n")
