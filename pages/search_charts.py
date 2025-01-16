import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
import datetime
import plotly.graph_objects as go
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler

st.title("차트 검색")

# LSTM 모델 로드
model = tf.keras.models.load_model('./model/keras_model_삼성전자.h5')

# Scaler 설정
scaler = MinMaxScaler()

# 주가 정보 가져오기
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

# 종목 코드 찾기
def get_ticker_symbol(company_name):
    df = get_stock_info()
    code = df[df['회사명'] == company_name]['종목코드'].values
    return code[0] if len(code) > 0 else None

# 충분한 과거 데이터를 확보하는 함수
def load_two_years_data(ticker_symbol, today):
    start_date = today - datetime.timedelta(days=730)  # 2년 전
    df = fdr.DataReader(f'KRX:{ticker_symbol}', start_date, today)
    df = df[['Close']]
    return df

# 종목 검색 및 선택
stock_info = get_stock_info()
search_term = st.text_input("종목 검색 (회사명 입력)", key="search_stock")
filtered_stocks = stock_info[stock_info["회사명"].str.contains(search_term, na=False)] if search_term else stock_info

if not filtered_stocks.empty:
    stock_name = st.selectbox("검색 결과", filtered_stocks["회사명"], key="selected_stock")

date_range = [st.date_input('시작일 입력', max_value= datetime.datetime.now()  - datetime.timedelta(days=1)), st.date_input('종료일 입력')]

if stock_name and date_range[0] and date_range[1]:
    ticker_symbol = get_ticker_symbol(stock_name)
    start_p = date_range[0]
    end_p = date_range[1] + datetime.timedelta(days=1) 
    today = datetime.date.today()

    # 미래 예측
    if end_p > today:
        df = fdr.DataReader(f'KRX:{ticker_symbol}', start_p, today + datetime.timedelta(days=1))
        last_date = df.index.max()
        # 지난 2년간 데이터 불러오기
        past_2y_data = load_two_years_data(ticker_symbol, today)
        # 스케일링
        scaler = MinMaxScaler()
        scaled_data = scaler.fit_transform(past_2y_data)

        x = []
        for i in range(len(scaled_data) - 100):
            x.append(scaled_data[i:i + 100])
        x = np.array(x)
        last_sequence = scaled_data[-100:]
        future_predictions = []

        predict_days = (end_p - today).days
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
    else:
        df = fdr.DataReader(f'KRX:{ticker_symbol}', start_p, end_p)
        future_df = pd.DataFrame()

    ## 표 이름 한글로 수정
    df.rename(columns={
        'Date': '날짜',
        'Close': '종가',
        'Open': '시가',
        'High': '고가',
        'Low' : '저가',
        'Volume': '거래량',
        'Change': '변동률',
        'UpDown': '상승/하락',
        'Comp': '비교',
        'Amount': '금액',
        'MarCap': '시가총액',
        'Shares': '발행주식수'
    }, inplace=True)

    # 변경된 데이터 출력
    st.subheader(f"{stock_name} 주가 데이터")
    st.dataframe(df)

    # 그래프
    fig = go.Figure()

    ## 종가(Close) 라인 차트 추가
    fig.add_trace(go.Scatter(x=df.index, y=df['종가'],
                         mode='lines',
                         name='종가'))

    # 캔들 차트 추가
    if '시가' in df.columns:
        fig.add_trace(go.Candlestick(x=df.index,
                                 open=df['시가'],
                                 high=df['고가'],
                                 low=df['저가'],
                                 close=df['종가'],
                                 name='켄들 스틱'))

    # 예측 주가 라인 (빨간색)
    if not future_df.empty:
        fig.add_trace(go.Scatter(x=future_df.index, y=future_df['Close'],
                                 mode='lines',
                                 name='예측 종가',
                                 line=dict(color='red', dash='dot')))

    fig.update_layout(title=f'{stock_name} 주가 데이터',
                      xaxis_title='Date',
                      yaxis_title='Price (KRW)',
                      template='plotly_dark')
    
    st.plotly_chart(fig, use_container_width=True)
