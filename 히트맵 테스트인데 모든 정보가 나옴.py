import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# [설정]
TARGET_SCORE = 3
P = 0.53  # A팀 세트 승률
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

def get_full_analysis(target, p):
    # 데이터 저장용 행렬들
    size = target 
    mat_prob = np.zeros((size, size))      # 1. 승률
    mat_imp = np.zeros((size, size))       # 2. 중요도
    mat_dur = np.zeros((size, size))       # 3. 기대 잔여 세트
    mat_score = [["" for _ in range(size)] for _ in range(size)] # 4. 최빈 스코어

    # DP 테이블 생성 (승률 계산용)
    dp = [[0.0] * (target + 1) for _ in range(target + 1)]
    for b in range(target + 1): 
        dp[target][b] = 1.0 # A승리 확정
    for a in range(target + 1): 
        dp[a][target] = 0.0 # A패배 확정 (이미 0이지만 명시)
    
    # 승률 역산
    for a in range(target - 1, -1, -1):
        for b in range(target - 1, -1, -1):
            dp[a][b] = p * dp[a+1][b] + (1-p) * dp[a][b+1]

    # 각 셀(스코어)별 분석 수행
    for a in range(size):
        for b in range(size):
            # 1. 매치 승률
            cur_prob = dp[a][b]
            mat_prob[a][b] = cur_prob * 100

            # 2. 중요도 (Leverage)
            if_win = dp[a+1][b]
            if_loss = dp[a][b+1]
            mat_imp[a][b] = (if_win - if_loss) * 100

            # 3 & 4. 기대 듀레이션 및 최빈 스코어 (별도 시뮬레이션 필요)
            # 해당 시점(a,b)에서 시작하는 서브 게임 시뮬레이션
            reach = np.zeros((target + 1, target + 1))
            reach[a][b] = 1.0
            
            # 전진 계산
            for i in range(a, target + 1):
                for j in range(b, target + 1):
                    if i == target or j == target: 
                        continue
                    if reach[i][j] > 0:
                        reach[i+1][j] += reach[i][j] * p
                        reach[i][j+1] += reach[i][j] * (1-p)
            
            # 결과 집계
            expected_sets = 0
            max_prob = -1
            most_likely_str = ""
            
            # 최종 상태 도달 확률 확인
            # A승리 케이스 (3:0, 3:1, 3:2)
            for y in range(b, target):
                prob_end = reach[target][y]
                if prob_end > 0:
                    sets_played = (target + y) - (a + b)
                    expected_sets += sets_played * prob_end
                    if prob_end > max_prob:
                        max_prob = prob_end
                        most_likely_str = f"A승\n{target}:{y}"

            # B승리 케이스 (0:3, 1:3, 2:3)
            for x in range(a, target):
                prob_end = reach[x][target]
                if prob_end > 0:
                    sets_played = (x + target) - (a + b)
                    expected_sets += sets_played * prob_end
                    if prob_end > max_prob:
                        max_prob = prob_end
                        most_likely_str = f"B승\n{x}:{target}"
            
            mat_dur[a][b] = expected_sets
            mat_score[a][b] = most_likely_str

    return mat_prob, mat_imp, mat_dur, mat_score

# 데이터 계산
m_prob, m_imp, m_dur, m_score = get_full_analysis(TARGET_SCORE, P)

# --- 시각화 (4분할 대시보드) ---
fig, axes = plt.subplots(2, 2, figsize=(14, 12))
fig.suptitle(f'Best of 5 전략 대시보드 (A팀 세트 승률: {P*100}%)', fontsize=20, weight='bold')

# 공통 설정
x_labels = [f"B {i}승" for i in range(TARGET_SCORE)]
y_labels = [f"A {i}승" for i in range(TARGET_SCORE)]

# 1. 매치 승률 (Win Probability)
sns.heatmap(m_prob, ax=axes[0,0], annot=True, fmt=".1f", cmap="RdYlGn", vmin=0, vmax=100)
axes[0,0].set_title("[1] 매치 승리 확률 (%)", fontsize=14, weight='bold')
axes[0,0].set_ylabel("현재 유리함 <---> 불리함")

# 2. 중요도 (Leverage)
sns.heatmap(m_imp, ax=axes[0,1], annot=True, fmt=".1f", cmap="Reds")
axes[0,1].set_title("[2] 승부처 중요도 (Leverage)", fontsize=14, weight='bold')
axes[0,1].set_ylabel("변동성 낮음 <---> 높음")

# 3. 기대 잔여 세트 (Duration)
sns.heatmap(m_dur, ax=axes[1,0], annot=True, fmt=".2f", cmap="Blues")
axes[1,0].set_title("[3] 기대 잔여 세트 수 (Duration)", fontsize=14, weight='bold')
axes[1,0].set_ylabel("자금 회수 빠름 <---> 느림")

# 4. 최빈 최종 스코어 (Most Likely Outcome)
# 히트맵 대신 텍스트 그리드로 표현
sns.heatmap(np.zeros((3,3)), ax=axes[1,1], annot=np.array(m_score), fmt="", cmap="Greys", cbar=False,
            annot_kws={"size": 14})
axes[1,1].set_title("[4] 가장 유력한 최종 스코어", fontsize=14, weight='bold')

# 축 레이블 정리 (모든 그래프 공통)
for ax in axes.flat:
    ax.set_xticklabels(x_labels)
    ax.set_yticklabels(y_labels)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()