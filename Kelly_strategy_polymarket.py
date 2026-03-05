# [설정 영역]
win_prob = 0.9  # 내가 생각하는 승률 (0~1 사이 값)
market_price = 0.77  # 시장가 (0~1 사이 값)


def calculate_kelly_polymarket(win_prob, market_price):
    """
    켈리 비율을 폴리마켓에 맞춘 계산기

    Parameters:
    -----------
    win_prob: 내가 생각하는 승률 (0과 1 사이의 값)
    market_price : 시장가 (0과 1 사이의 값)

    Returns:
    --------
        베팅해야 할 자본의 비율 (0과 1 사이의 값)
        음수인 경우 베팅하지 않는 것이 유리함
    """

    # 켈리 공식 about 폴리마켓 계산
    # f = (win_prob-market_price) / (1-market_price)
    # win_prob : 승률 (0과 1 사이의 값)
    # market_price : 시장가 (0과 1 사이의 값)

    kelly_fraction_polymarket = (win_prob - market_price) / (1 - market_price)

    return kelly_fraction_polymarket


full_kelly_polymarket = calculate_kelly_polymarket(win_prob, market_price)

print(f"켈리 비율: {int(full_kelly_polymarket * 100)}%")
print(f"하프 켈리 비율: {int((full_kelly_polymarket * 0.5) * 100)}%")
print(f"쿼터 켈리 비율: {int((full_kelly_polymarket * 0.25) * 100)}%")
