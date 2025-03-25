import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import FinanceDataReader as fdr
import os
from openai import OpenAI
import openai
import plotly.graph_objects as go
import datetime
from dotenv import load_dotenv

# Streamlit 페이지 제목
st.title("AI 종목 분석📈")
st.markdown("#### 분석을 원하는 종목을 AI에게 물어보세요✨")

# 주의점 popover 추가
with st.popover(label="ℹ️주의사항", use_container_width=True):
    st.markdown("**모든 투자의 책임은 전적으로 투자자 본인에게 있습니다.**")

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
if not openai_api_key:
    print("OpenAI API 키가 로드되지 않았습니다.")
else:
    print("OpenAI API 키 로드 성공!")

client = OpenAI(api_key=openai_api_key)

# 사용자 입력 (종목명)
prompt = st.chat_input("종목 입력")

if openai_api_key and prompt:
    try:
        

        stock_name = prompt  # 채팅 입력을 종목명으로 사용

        # 종목 정보 가져오기
        @st.cache_data
        def get_stock_info():
            base_url = "http://kind.krx.co.kr/corpgeneral/corpList.do"
            method = "download"
            url = f"{base_url}?method={method}"
            df = pd.read_html(url, header=0, encoding='cp949')[0]
            df['종목코드'] = df['종목코드'].apply(lambda x: f"{x:06d}")
            df = df[['회사명', '종목코드']]
            return df

        def get_ticker_symbol(company_name):
            df = get_stock_info()
            code = df[df['회사명'] == company_name]['종목코드'].values
            if len(code) == 0:
                st.error("종목명을 찾을 수 없습니다. 다시 입력해주세요.")
                st.stop()
            return code[0]

        @st.cache_data
        def get_financial_data(ticker):
            try:
                stock_info = fdr.DataReader(ticker)
                latest_price = stock_info["Close"].iloc[-1]
                return {"ticker": ticker, "latest_price": latest_price}
            except Exception as e:
                return {"error": str(e)}

        def get_stock_news(keyword):
            base_url = f"https://search.naver.com/search.naver?where=news&query={keyword}&sm=tab_tmr"
            response = requests.get(base_url)
            soup = BeautifulSoup(response.text, "html.parser")
            articles = []
            for item in soup.select(".news_tit"):
                title = item["title"]
                link = item["href"]
                articles.append({"title": title, "link": link})
            return articles

        def get_analysis_report(ticker):
            """
            AI가 종목 분석 리포트를 생성함
            """
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "너는 주식 데이터 분석 전문가야."},
                    {"role": "user", "content": f"{ticker} 종목의 최근 뉴스 및 데이터를 기반으로. \
                    앞으로의 주가 전망에 대해 5줄 이내 리포트써줘. 종목 코드는 말 안해도 돼. \
                    글자 크기는 최대 15pt 이내로 써줘. 마지막에 이 종목을 **추천하는지 비추천하는지** 판단해서 문장 넣어줘. "}
                ]
            )
            return response.choices[0].message.content

        ticker_symbol = get_ticker_symbol(stock_name)

        # 날짜 계산 (최근 한 달)
        end_p = datetime.date.today()
        start_p = end_p - datetime.timedelta(days=30)

        # 주가 데이터 가져오기
        df = fdr.DataReader(f'KRX:{ticker_symbol}', start_p, end_p)
        df.index = df.index.date

        # 주가 데이터 표출
        st.subheader(f"최근 일주일간 {stock_name}의 주가 데이터")
        st.dataframe(df.tail(7))

        # 주가 차트 생성
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close Price'))
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Candlestick'))
        fig.update_layout(title=f'{stock_name} Stock Price',
                          xaxis_title='Date',
                          yaxis_title='Price (KRW)',
                          xaxis_rangeslider_visible=False,
                          template='plotly_dark')
        st.plotly_chart(fig, use_container_width=True)

        # AI 분석 리포트
        st.subheader(f"{stock_name} AI 분석 리포트🤖")
        report = get_analysis_report(ticker_symbol)
        st.write(report)

        # 뉴스 크롤링 결과
        st.subheader(f"{stock_name}의 관련 뉴스 및 참고자료")
        news = get_stock_news(stock_name)
        if news:
            for article in news:
                st.write(f"- [{article['title']}]({article['link']})")
        else:
            st.write("관련 뉴스를 가져올 수 없습니다.")
    
    except Exception as e:
        st.error(f"⚠️ 오류가 발생했습니다: {e}")
else:
    if not openai_api_key:
        st.warning("🔑 OpenAI API 키를 입력하세요.")
    elif not prompt:
        st.warning("📊 분석할 종목명을 입력하세요.")
