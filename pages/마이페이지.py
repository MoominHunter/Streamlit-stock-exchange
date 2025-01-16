import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import date, timedelta
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from matplotlib import rc

# 그래프 폰트
plt.rcParams['font.family'] = 'Malgun Gothic'


@st.cache_data
def get_historical_prices(stock_name, start_date, end_date):
    """종목의 과거 가격 가져오기"""
    try:
        return fdr.DataReader(stock_name, start_date, end_date)
    except Exception:
        return pd.DataFrame()

# UI
st.title("마이페이지")
user = st.session_state.user1

# 현재 자산 계산
total_stock_value = sum(stock.purchase_price * stock.count for stock in user.stocks)
total_asset = user.money + total_stock_value

# 사용자 정보 표시
st.subheader("현재 자산 상황")
st.write(f"👤 이름: {user.name}")
st.write(f"💼 총 자산: {total_asset:,}원")
st.write(f"💰 현금 자산: {user.money:,}원")

# 보유 주식 요약
st.subheader("보유 종목 요약")
if user.stocks:
    stock_df = pd.DataFrame(user.stocks)
    stock_df["자산 가치"] = stock_df["purchase_price"] * stock_df["count"]
    st.dataframe(stock_df[["name", "count", "purchase_price", "자산 가치"]], use_container_width=True)
else:
    st.write("보유 종목이 없습니다.")

# 종목 비중
st.subheader("종목 비중")
portfolio = {stock["name"]: stock["purchase_price"] * stock["count"] for stock in user.stocks}
portfolio["현금"] = user.money

# Plotly Pie Chart
fig1 = px.pie(
    names=portfolio.keys(),
    values=portfolio.values(),
    title="포트폴리오 비중",
    hole=0.3,  # 도넛 차트 스타일
)

fig1.update_traces(textinfo="percent+label")  # 퍼센트와 라벨 표시
fig1.update_layout(
    showlegend=True,
    legend_title="항목",
    template="plotly_white"
)

st.plotly_chart(fig1, use_container_width=True)

# 누적 자산 변동
st.subheader("누적 자산 변동")
start_date = st.date_input("시작 날짜", value=date.today() - timedelta(days=30))
end_date = st.date_input("종료 날짜", value=date.today())

historical_df = pd.DataFrame()
for stock in user.stocks:
    df = get_historical_prices(stock.name, start_date, end_date)
    if not df.empty:
        df["name"] = stock.name
        df["quantity"] = stock.count
        df["value"] = df["Close"] * stock.count
        historical_df = pd.concat([historical_df, df])

if not historical_df.empty:
    historical_df.reset_index(inplace=True)
    historical_df.rename(columns={"index": "날짜"}, inplace=True)
    total_historical = historical_df.groupby("날짜")["value"].sum().reset_index()
    total_historical["total_asset"] = total_historical["value"] + user.money

    # 데이터 요약
    max_asset = total_historical["total_asset"].max()
    min_asset = total_historical["total_asset"].min()
    current_asset = total_historical["total_asset"].iloc[-1]
    st.write(f"📈 최대 자산: {max_asset:,.0f}원")
    st.write(f"📉 최소 자산: {min_asset:,.0f}원")
    st.write(f"💼 현재 자산: {current_asset:,.0f}원")

    # 그래프 생성
    fig2 = go.Figure()

    # 누적 자산 라인
    fig2.add_trace(go.Scatter(
        x=total_historical["날짜"],
        y=total_historical["total_asset"],
        mode="lines+markers",
        name="총 자산",
        line=dict(color="green"),
    ))

    # 기준선 (초기 자산)
    initial_asset = total_historical["total_asset"].iloc[0]
    fig2.add_trace(go.Scatter(
        x=total_historical["날짜"],
        y=[initial_asset] * len(total_historical),
        mode="lines",
        name="초기 자산",
        line=dict(dash="dash", color="gray"),
    ))

    # 주석 추가 (최대/최소)
    fig2.add_annotation(
        x=total_historical.loc[total_historical["total_asset"].idxmax(), "날짜"],
        y=max_asset,
        text=f"최대: {max_asset:,.0f}원",
        showarrow=True,
        arrowhead=2,
        font=dict(color="red"),
    )
    fig2.add_annotation(
        x=total_historical.loc[total_historical["total_asset"].idxmin(), "날짜"],
        y=min_asset,
        text=f"최소: {min_asset:,.0f}원",
        showarrow=True,
        arrowhead=2,
        font=dict(color="blue"),
    )

    # 그래프 레이아웃
    fig2.update_layout(
        title="누적 자산 변동",
        xaxis_title="날짜",
        yaxis_title="총 자산 (KRW)",
        template="plotly_white",
    )

    st.plotly_chart(fig2, use_container_width=True)
else:
    st.write("누적 자산 변동 데이터를 가져올 수 없습니다.")
   
