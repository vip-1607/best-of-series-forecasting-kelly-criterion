# 상대가치투자
import numpy as np

class Bo3Analyzer:
    def __init__(self, match_odds_team_a, match_odds_team_b):
        # 1. 수수료(Vig) 제거 및 내재 확률 계산
        prob_a = 1 / match_odds_team_a
        prob_b = 1 / match_odds_team_b
        total_prob = prob_a + prob_b
        
        # 실제 확률 (True Probability) 정규화
        self.p_match_a = prob_a / total_prob
        
        # 2. 세트 승률(p) 역산 (3p^2 - 2p^3 = Match_Prob)
        # 방정식: -2p^3 + 3p^2 + 0p - Match_Prob = 0
        coeffs = [-2, 3, 0, -self.p_match_a]
        roots = np.roots(coeffs)
        
        # 0~1 사이의 실수해만 추출
        self.p_set = [r.real for r in roots if np.isreal(r) and 0 <= r.real <= 1][0]

    def get_analysis(self):
        p = self.p_set
        q = 1 - p
        
        # 이론적 확률 계산
        prob_2_0 = p * p             # -1.5 핸디캡 승리 확률
        prob_over_2_5 = 2 * p * q    # 2.5 오버 확률
        
        return {
            "내재_세트_승률(p)": round(p, 4),
            "적정_핸디캡_배당(-1.5)": round(1 / prob_2_0, 2),
            "적정_오버_배당(2.5)": round(1 / prob_over_2_5, 2)
        }

# --- 실행 예시 ---
# A팀 승 1.40 vs B팀 승 2.80
analyzer = Bo3Analyzer(match_odds_team_a=1.40, match_odds_team_b=2.80)
result = analyzer.get_analysis()

print(f"📊 분석 결과: {result}")
# 만약 실제 사이트의 핸디캡 배당이 '적정_핸디캡_배당'보다 높다면? -> 매수 기회!