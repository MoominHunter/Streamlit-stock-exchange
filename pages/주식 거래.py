
import streamlit as st
import FinanceDataReader as fdr
import tensorflow as tf
import plotly.graph_objects as go
import pandas as pd
import datetime
import requests
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# LSTM 모델 로드
model = tf.keras.models.load_model('./model/keras_model_삼성전자.h5')

# Scaler 설정
scaler = MinMaxScaler()

try:
    # API 요청
    response = requests.get("https://api.ivl.is/hangangtemp/")
    response.raise_for_status()  # HTTP 에러 확인

    # JSON 데이터 파싱
    data = response.json()

    # 결과 출력
    st.subheader(f"지금 한강물, {data['temperature']}℃")
    st.write(f"{data['date'][:4]}년 {data['date'][4:6]}월 {data['date'][6:]}일  {data['time']}시 {data['location']}에서 가져온 정보입니다.")
except requests.exceptions.RequestException as e:
    st.error(f"API 호출 실패: {e}")


@st.cache_data
def get_stock_info():
    """KRX 상장 종목 정보를 가져오기"""
    base_url = "http://kind.krx.co.kr/corpgeneral/corpList.do"
    method = "download"
    url = f"{base_url}?method={method}"
    stock_info = pd.read_html(url, header=0, encoding="cp949")[0]
    stock_info["종목코드"] = stock_info["종목코드"].apply(lambda x: f"{x:06d}")
    stock_info = stock_info[["회사명", "종목코드"]]
    return stock_info

@st.cache_data
def get_stock_price(stock_code):
    """FinanceDataReader를 이용해 특정 종목의 현재 주가를 가져오기"""
    try:
        today = datetime.date.today()
        df = fdr.DataReader(stock_code, today - datetime.timedelta(days=1), today)
        if not df.empty:
            return df["Close"][-1]
        else:
            return None
    except Exception:
        return None
    
# 충분한 과거 데이터를 확보하는 함수
def load_two_years_data(ticker_symbol, today):
    start_date = today - datetime.timedelta(days=730)  # 2년 전
    df = fdr.DataReader(f'KRX:{ticker_symbol}', start_date, today)
    df = df[['Close']]
    return df

# UI
st.title("주식 거래")
user = st.session_state.user1

# Tabs for Buy and Sell
tab1, tab2 = st.tabs(["📈 주식 매수", "📉 주식 매도"])

# 종목 검색 및 선택
stock_info = get_stock_info()
search_term = st.text_input("종목 검색 (회사명 입력)", key="search_stock")
filtered_stocks = stock_info[stock_info["회사명"].str.contains(search_term, na=False)] if search_term else stock_info

if not filtered_stocks.empty:
    selected_stock = st.selectbox("검색 결과", filtered_stocks["회사명"], key="selected_stock")
    selected_code = filtered_stocks[filtered_stocks["회사명"] == selected_stock]["종목코드"].values[0]
    stock_price = get_stock_price(selected_code)

    with tab1:
        # 매수 화면
        st.subheader("📈 주식 매수")
        if stock_price:
            st.info(f"{selected_stock} ({selected_code})의 현재 주가: {stock_price:,}원")
            buy_count = st.number_input("매수 수량", min_value=1, step=1, key="buy_count")
            future_date = datetime.date.today() + datetime.timedelta(days=7)
            # 그래프
            df = fdr.DataReader(f'KRX:{selected_code}', datetime.date.today() - datetime.timedelta(days=31), datetime.date.today() + datetime.timedelta(days=1))
            last_date = df.index.max()

            # 지난 2년간 데이터 불러오기
            today = datetime.date.today()
            past_2y_data = load_two_years_data(selected_code, today)
            # 스케일링
            scaler = MinMaxScaler()
            scaled_data = scaler.fit_transform(past_2y_data)

            x = []
            for i in range(len(scaled_data) - 100):
                x.append(scaled_data[i:i + 100])
            x = np.array(x)
            last_sequence = scaled_data[-100:]
            future_predictions = []

            predict_days = (future_date - today).days
            for _ in range(predict_days):
                # 모델로 예측
                next_scaled = model.predict(last_sequence[np.newaxis, :, :])
                future_predictions.append(next_scaled[0, 0])

                # 새로운 값 추가 후 시퀀스 업데이트
                next_scaled_sequence = np.vstack([last_sequence[1:], next_scaled.reshape(1, -1)])
                last_sequence = next_scaled_sequence
            # 예측값 스케일 복원
            future_predictions = scaler.inverse_transform(np.array(future_predictions).reshape(-1, 1))

            # future_predictions 조정
            adjustment_value = future_predictions[0, 0] - df['Close'].iloc[-1]
            future_predictions -= adjustment_value

            # 예측 정리
            future_dates = [last_date + datetime.timedelta(days=i) for i in range(0, predict_days)]
            future_df = pd.DataFrame({'Close': future_predictions.flatten()}, index=future_dates)

            fig = go.Figure()

            ## 종가(Close) 라인 차트 추가
            fig.add_trace(go.Scatter(x=df.index, y=df['Close'],
                                mode='lines',
                                name='Close Price'))

            # 캔들 차트 추가
            if 'Open' in df.columns:
                fig.add_trace(go.Candlestick(x=df.index,
                                        open=df['Open'],
                                        high=df['High'],
                                        low=df['Low'],
                                        close=df['Close'],
                                        name='Candlestick'))
            
            # 예측 주가 라인 (빨간색)
            if not future_df.empty:
                fig.add_trace(go.Scatter(x=future_df.index, y=future_df['Close'],
                                        mode='lines',
                                        name='예측 종가',
                                        line=dict(color='red', dash='dot')))
            
            fig.update_layout(title=f'매도 날짜 {selected_stock} 주가 예측값',
                    xaxis_title='Date',
                    yaxis_title='Price (KRW)',
                    template='plotly_dark')
            
            st.plotly_chart(fig, use_container_width=True)

            if st.button("주식 구매"):
                result = user.buy_stock(selected_stock, stock_price, buy_count)
                if "잔액 부족" in result:
                    st.error(result)  # 구매 실패 메시지
                else:
                    st.success(result)  # 구매 성공 메시지
        else:
            st.warning("현재 주가를 가져올 수 없습니다.")

    with tab2:
        # 매도 화면
        st.subheader("📉 주식 매도")
        if stock_price:
            st.info(f"{selected_stock} ({selected_code})의 현재 주가: {stock_price:,}원")
            sell_count = st.number_input("매도 수량", min_value=1, step=1, key="sell_count")
            sell_date = st.date_input("매도 날짜 선택", value=datetime.date.today() + datetime.timedelta(days=1) , min_value= datetime.date.today() + datetime.timedelta(days=1),  key="sell_date")

            # 그래프
            if sell_date:
                df = fdr.DataReader(f'KRX:{selected_code}', datetime.date.today() - datetime.timedelta(days=31), datetime.date.today() + datetime.timedelta(days=1))
                last_date = df.index.max()
                # 지난 2년간 데이터 불러오기
                today = datetime.date.today()
                past_2y_data = load_two_years_data(selected_code, today)
                # 스케일링
                scaler = MinMaxScaler()
                scaled_data = scaler.fit_transform(past_2y_data)

                x = []
                for i in range(len(scaled_data) - 100):
                    x.append(scaled_data[i:i + 100])
                x = np.array(x)
                last_sequence = scaled_data[-100:]
                future_predictions = []

                predict_days = (sell_date - today).days
                for _ in range(predict_days):
                    # 모델로 예측
                    next_scaled = model.predict(last_sequence[np.newaxis, :, :])
                    future_predictions.append(next_scaled[0, 0])

                    # 새로운 값 추가 후 시퀀스 업데이트
                    next_scaled_sequence = np.vstack([last_sequence[1:], next_scaled.reshape(1, -1)])
                    last_sequence = next_scaled_sequence
                # 예측값 스케일 복원
                future_predictions = scaler.inverse_transform(np.array(future_predictions).reshape(-1, 1))

                # future_predictions 조정
                adjustment_value = future_predictions[0, 0] - df['Close'].iloc[-1]
                future_predictions -= adjustment_value

                # 예측 정리
                future_dates = [last_date + datetime.timedelta(days=i) for i in range(0, predict_days)]
                future_df = pd.DataFrame({'Close': future_predictions.flatten()}, index=future_dates)


                fig = go.Figure()

                ## 종가(Close) 라인 차트 추가
                fig.add_trace(go.Scatter(x=df.index, y=df['Close'],
                                    mode='lines',
                                    name='종가'))

                # 캔들 차트 추가
                if 'Open' in df.columns:
                    fig.add_trace(go.Candlestick(x=df.index,
                                            open=df['Open'],
                                            high=df['High'],
                                            low=df['Low'],
                                            close=df['Close'],
                                            name='캔들 스틱'))
                # 예측 주가 라인 (빨간색)
                if not future_df.empty:
                    fig.add_trace(go.Scatter(x=future_df.index, y=future_df['Close'],
                                            mode='lines',
                                            name='예측 종가',
                                            line=dict(color='red', dash='dot')))
                
                fig.update_layout(title=f'매도 날짜 {selected_stock} 주가 예측값',
                        xaxis_title='Date',
                        yaxis_title='Price (KRW)',
                        template='plotly_dark')
                
                st.plotly_chart(fig, use_container_width=True)

            if st.button("주식 판매"):
                result = user.sell_stock(selected_stock, stock_price, sell_count)
                if "보유하고 있지 않습니다" in result or "없습니다" in result:
                    st.error(result)  # 매도 실패 메시지
                else:
                    st.success(result)  # 매도 성공 메시지
        else:
            st.warning("현재 주가를 가져올 수 없습니다.")

else:
    st.write("검색 결과가 없습니다.")