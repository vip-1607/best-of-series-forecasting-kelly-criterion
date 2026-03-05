# ===================== [설정 영역] =====================
INITIAL_INVEST = 100.0  # 초기 투자금 ($)
ENTRY_PRICE = 40  # 초기 진입 가격 (센트, 1 ~ 99)
CURRENT_HEDGE_PRICE = 20  # 현재 반대편(Hedge) 옵션 가격 (센트, 1 ~ 99)
HEDGE_RATIO = 0.5  # 헷지 비율 (1.0 = 완전 프리롤, 0.5 = 원금 50% 보장)
# ========================================================


def calculate_free_roll(initial_invest, initial_price, hedge_price):
    """
    완전 프리 롤(손실 0원) 헷징 계산기

    Parameters:
        initial_invest (float): 초기 투자금 ($)
        initial_price (float): 초기 진입 가격 (0.01 ~ 0.99, 센트 값을 100으로 나눈 값)
        hedge_price (float): 현재 반대편(Hedge) 옵션 가격 (0.01 ~ 0.99, 센트 값을 100으로 나눈 값)

    Returns:
        dict: 헷징 전략 결과 데이터
    """
    # 헷징에 필요한 주식 수 (공식: 원금 / (1 - 헷지단가))
    # N * 1.0 = Initial + (N * Hedge_Price) → N = Initial / (1 - Hedge_Price)
    hedge_shares = initial_invest / (1 - hedge_price)

    # 헷징 비용 계산
    hedge_cost = hedge_shares * hedge_price

    # 총 비용 (Total Cost)
    total_cost = initial_invest + hedge_cost

    # 시나리오별 수익 계산
    initial_shares = initial_invest / initial_price

    # 시나리오 A: 원래 건 팀(Main) 승리 시
    profit_main_win = (initial_shares * 1.0) - total_cost

    # 시나리오 B: 반대 팀(Hedge) 승리 시
    profit_hedge_win = (hedge_shares * 1.0) - total_cost

    return {
        "initial_shares": round(initial_shares, 2),
        "hedge_shares": round(hedge_shares, 2),
        "hedge_cost": round(hedge_cost, 2),
        "total_cost": round(total_cost, 2),
        "profit_main_win": round(profit_main_win, 2),
        "profit_hedge_win": round(profit_hedge_win, 2),
        "is_profitable": profit_main_win > 0,
    }


def calculate_partial_hedge(
    initial_invest, initial_price, hedge_price, hedge_ratio=1.0
):
    """
    부분 헷징 계산기

    hedge_ratio를 조절하여 보험 범위를 선택합니다:
        1.0  = 완전 프리 롤 (손실 0원, 원금 100% 보장)
        0.75 = 원금의 75%만 보장 (보험료 절약, 수익 증가)
        0.50 = 원금의 50%만 보장 (보험료 더 절약)

    핵심 공식:
        완전 프리 롤:  N = initial_invest / (1 - hedge_price)
        부분 헷징:     N = (initial_invest × hedge_ratio) / (1 - hedge_price)

    Parameters:
        initial_invest (float): 초기 투자금 ($)
        initial_price (float): 초기 진입 가격 (0.01 ~ 0.99, 센트 값을 100으로 나눈 값)
        hedge_price (float): 현재 반대편(Hedge) 옵션 가격 (0.01 ~ 0.99, 센트 값을 100으로 나눈 값)
        hedge_ratio (float): 헷지 비율 (0.0 ~ 1.0, 기본값: 1.0)

    Returns:
        dict: 부분 헷징 전략 결과 데이터
    """
    # 부분 헷징: 보장할 원금 비율만큼만 헷지 주식 매수
    protected_amount = initial_invest * hedge_ratio
    hedge_shares = protected_amount / (1 - hedge_price)

    # 비용 계산
    hedge_cost = hedge_shares * hedge_price
    total_cost = initial_invest + hedge_cost

    # 시나리오별 수익 계산
    initial_shares = initial_invest / initial_price

    # 시나리오 A: Main 승리 시
    profit_main_win = (initial_shares * 1.0) - total_cost

    # 시나리오 B: Hedge 승리 시
    profit_hedge_win = (hedge_shares * 1.0) - total_cost

    return {
        "hedge_ratio": hedge_ratio,
        "protected_amount": round(protected_amount, 2),
        "initial_shares": round(initial_shares, 2),
        "hedge_shares": round(hedge_shares, 2),
        "hedge_cost": round(hedge_cost, 2),
        "total_cost": round(total_cost, 2),
        "profit_main_win": round(profit_main_win, 2),
        "profit_hedge_win": round(profit_hedge_win, 2),
        "is_profitable": profit_main_win > 0,
    }


def display_report(result, initial_invest, initial_price, hedge_price):
    """
    프리 롤 계산 결과 리포트 출력

    Parameters:
        result (dict): calculate_free_roll() 또는 calculate_partial_hedge()의 반환값
        initial_invest (float): 초기 투자금
        initial_price (float): 초기 진입 가격
        hedge_price (float): 헷지 가격
    """
    is_partial = "hedge_ratio" in result

    print(f"\n{'='*50}")
    if is_partial:
        ratio_pct = int(result["hedge_ratio"] * 100)
        print(f"  부분 헷징 리포트 (원금 {ratio_pct}% 보장)")
    else:
        print(f"  Free Roll Strategy Report (완전 프리 롤)")
    print(f"{'='*50}")

    print(f"\n[포지션 정보]")
    print(f"  초기 투자금:      ${initial_invest:.2f}")
    print(f"  진입 가격:        ${initial_price:.2f}")
    print(f"  보유 주식 수:     {result['initial_shares']:.2f}주")

    print(f"\n[헷지 정보]")
    print(f"  반대편 현재가:    ${hedge_price:.2f}")
    print(f"  헷지 매수량:      {result['hedge_shares']:.2f}주")
    print(f"  헷지 비용(보험료): ${result['hedge_cost']:.2f}")
    print(f"  총 투자금:        ${result['total_cost']:.2f}")

    # 합산가 판정
    combined = initial_price + hedge_price
    status = "[O] 수익 가능" if combined < 1.0 else "[X] 수익 불가"
    print(f"\n[합산가 판정]")
    print(f"  {initial_price} + {hedge_price} = ${combined:.2f}  {status}")

    print(f"\n{'-'*50}")
    print(f"[시나리오 분석]")

    # Main 승리
    sign_a = "+" if result["profit_main_win"] >= 0 else ""
    print(f"  Main 팀 승리 시:  {sign_a}${result['profit_main_win']:.2f}")

    # Hedge 승리
    sign_b = "+" if result["profit_hedge_win"] >= 0 else ""
    label_b = (
        "(본전)"
        if result["profit_hedge_win"] == 0
        else (
            "(원금 방어)"
            if result["profit_hedge_win"] > 0
            else "(제한 손실)" if is_partial else "(손실)"
        )
    )
    print(f"  Hedge 팀 승리 시: {sign_b}${result['profit_hedge_win']:.2f} {label_b}")

    print(f"{'-'*50}")

    # 경고 메시지
    if not result["is_profitable"]:
        print(
            f"\n  [!] [경고] 현재 가격으로는 프리 롤 구성 시 Main 승리해도 손실입니다!"
        )

    print(f"\n{'='*50}")


# ==========================================
# 메인 실행
# ==========================================
if __name__ == "__main__":

    # 센트 → 0~1 변환
    entry_price = ENTRY_PRICE / 100
    hedge_price = CURRENT_HEDGE_PRICE / 100

    # 1. 완전 프리 롤 계산
    result = calculate_free_roll(INITIAL_INVEST, entry_price, hedge_price)
    display_report(result, INITIAL_INVEST, entry_price, hedge_price)

    # 2. 부분 헷징 계산 (설정된 비율 사용)
    if HEDGE_RATIO < 1.0:
        partial = calculate_partial_hedge(
            INITIAL_INVEST, entry_price, hedge_price, HEDGE_RATIO
        )
        display_report(partial, INITIAL_INVEST, entry_price, hedge_price)
