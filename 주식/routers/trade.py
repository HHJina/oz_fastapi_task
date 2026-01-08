"""
거래 라우터 (Trade Router)
- 사용자 자산 상태 조회 및 매수/매도 로직 처리
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from models import User, Portfolio
from sqlalchemy import select

from .. import models
from .. import schemas
from ..auth import get_current_user
from ..database import get_db
from market import ConnectionManager

router = APIRouter()

manager = ConnectionManager()
@router.get("/user/status")
async def get_status(
    current_price: float,
    user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """자산 상태 조회"""
    # TODO: db.execute와 select를 사용해 유저의 Portfolio 정보를 조회하세요 (변수: result, p)
    # result = await db.execute(select(Portfolio).where(User.username == user.username))
    result = await db.execute(text("SELECT * FROM Portfolio WHERE username = :name"), {"name": user.username})
    p = result.all()

    # TODO: 포트폴리오 유무에 따라 보유수량(amount)과 평단가(avg_price)를 설정하세요
    # 특정 하나의 종목을 조회하는 로직인가? 전체 종목에 대해 조회하는 로직인가?
    if p:
        amount = p[0].amount
        avg_price = p[0].avg_price
    else:
        amount = 0
        avg_price = 0.0

    # TODO: 현재가 기준 평가금액(evaluation)과 평가손익(profit)을 계산하세요
    evaluation = amount * current_price
    total_purchase_price = amount * avg_price
    profit = total_purchase_price - evaluation

    # TODO: 다음 키를 가진 딕셔너리를 반환하세요:
    # "cash", "holdings", "evaluation", "profit", "total_asset"
    portfolio = {
        'cash': user.balance,
        'holdings': amount,
        'evaluation': evaluation,
        'profit': profit,
        'total_assets': user.balance + evaluation,
    }

    return portfolio


@router.post("/trade/{action}")
async def trade(
    action: str,
    payload: schemas.TradeRequest,
    user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """매수 및 매도 처리"""
    # TODO: 유저의 Portfolio 정보를 DB에서 조회하세요 (변수: result, p)
    result = await db.execute(
        text("SELECT * FROM portfolios WHERE username = :username AND symbol = :symbol"),
        {"username": user.username, "symbol": payload.symbol},
    )
    p = result.fetchone()

    if action == "buy":
        # TODO: cost(수량*가격) 계산 후 유저 잔액(user.balance) 부족 시 HTTPException 발생
        cost = payload.amount * payload.price
        if user.balance < cost:
            raise HTTPException(status_code=400, detail="잔액이 부족합니다.")

        # TODO: 유저 잔액 차감 및 포트폴리오(p) 업데이트
        # - 기존 데이터(p)가 있으면: 평단가(p.avg_price) 계산 로직 적용 및 수량 증가
        # - 없으면: 새로운 models.Portfolio 객체 생성(new_p) 후 db.add()
        user.balance -= cost

        if p:
            old_total = p.amount * p.price
            new_total = old_total + cost
            new_amount = p.amount + payload.amount
            new_avg_price = new_total / new_amount

            await db.execute(
                text("UPDATE portfolios SET amount = :amt, price = :price WHERE id = :id"),
                {"amt": new_amount, "price": new_avg_price, "id": p.id},
            )
        else:
            await db.execute(
                text("INSERT INTO portfolios (username, symbol, amount, price) VALUES (:name, :sym, :amt, :price)"),
                {"name": user.username,"sym": payload.symbol, "amt": payload.amount,"price": payload.price,},
            )

    elif action == "sell":
        # TODO: 포트폴리오 존재 여부와 수량(p.amount) 체크 후 부족 시 HTTPException 발생
        if not p or p.amount < payload.amount:
            raise HTTPException(status_code=400,detail=f"보유 수량이 부족합니다. (현재 보유: {p.amount}개)")

        # TODO: 유저 잔액(user.balance) 증가 및 포트폴리오 수량(p.amount) 차감
        # - 수량이 0이 되면 db.delete(p) 실행
        user.balance += (payload.amount * payload.price)
        new_amount = p.amount - payload.amount
        if new_amount == 0:
            await db.execute( text("DELETE FROM portfolios WHERE id = :id"),{"id": p.id})
        else:
            await db.execute(text("UPDATE portfolios SET amount = :amt WHERE id = :id"),{"amt": new_amount, "id": p.id})

    # TODO: db.commit()로 반영 후 manager.broadcast로 거래 알림을 전송하세요
    # 메시지 형식: {"type": "trade_news", "msg": f"🔔 {user.username}님 {action} 완료"}
    await db.commit()

    await manager.broadcast({
        "type": "trade_news",
        "msg": f"🔔 {user.username}님 {action} 완료"
    })

    return {"message": f"{action} 처리가 완료되었습니다."}