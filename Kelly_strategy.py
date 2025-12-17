def calculate_kelly(win_prob, odds, loss_rate):
    """
    켈리 비율 계산기
    
    Parameters:
    -----------
    win_prob: 승률 (0과 1 사이의 값)
    odds : 배당률 (예: 2.0은 1:1 배당, 3.0은 2:1 배당)
    loss_rate : 패배 시 순손실 비율 (1.0 = 100% 손실)
    
    Returns:
    --------
        베팅해야 할 자본의 비율 (0과 1 사이의 값)
        음수인 경우 베팅하지 않는 것이 유리함
    """
    
    # 켈리 공식 계산
    # f = (bp - aq) / (ab)
    a = loss_rate   # 순손실 비율
    b = odds - 1    # 순이익 비율
    p = win_prob    # 승리 확률
    q = 1 - p       # 패배 확률
    
    kelly_fraction = (b * p - a * q) / (a * b)
    
    return kelly_fraction

# ==========================================
# ⚙️ [설정 영역]
# ==========================================
win_prob = 0.77   # 승률 (0~1 사이 값)
odds = 2.0        # 배당률
loss_rate = 1.0   # 패배 시 순손실 비율 (기본값: 1.0 = 100% 손실)
# ==========================================

full_kelly = calculate_kelly(win_prob, odds, loss_rate)

print(f"켈리 비율: {int(full_kelly * 100)}%")
print(f"하프 켈리 비율: {int((full_kelly * 0.5) * 100)}%")
print(f"쿼터 켈리 비율: {int((full_kelly * 0.25) * 100)}%")