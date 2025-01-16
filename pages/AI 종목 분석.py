import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import FinanceDataReader as fdr
import openai
import plotly.graph_objects as go

# Streamlit 페이지 제목
st.title("AI 종목 분석📈")

st.markdown("#### 분석을 원하는 종목을 AI에게 물어보세요✨")

# 사용자 입력
prompt = st.chat_input("종목 입력")

if prompt:
    stock_name = prompt  # 채팅 입력을 종목명으로 사용

    # caching
    # 인자가 바뀌지 않는 함수 실행 결과를 저장 후 크롬의 임시 저장 폴더에 저장 후 재사용
    @st.cache_data
    def get_stock_info():
        base_url =  "http://kind.krx.co.kr/corpgeneral/corpList.do"    
        method = "download"
        url = "{0}?method={1}".format(base_url, method)   
        df = pd.read_html(url, header=0, encoding= 'cp949')[0]
        df['종목코드']= df['종목코드'].apply(lambda x: f"{x:06d}")     
        df = df[['회사명','종목코드']]
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
            # 주식 시세 데이터 가져오기
            stock_info = fdr.DataReader(ticker)
            latest_price = stock_info["Close"].iloc[-1]
            return {"ticker": ticker, "latest_price": latest_price}
        except Exception as e:
            return {"error": str(e)}


    def get_stock_news(keyword):
        """
        네이버 뉴스에서 해당 키워드 관련 뉴스 크롤링
        """
        base_url = f"https://search.naver.com/search.naver?where=news&query={keyword}&sm=tab_tmr"
        response = requests.get(base_url)
        soup = BeautifulSoup(response.text, "html.parser")

        articles = []
        for item in soup.select(".news_tit"):
            title = item["title"]
            link = item["href"]
            articles.append({"title": title, "link": link})

        return articles

    #과금에 필요한 API키 지정
    client = openai.OpenAI(api_key = "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")

    def get_analysis_report(ticker):
        """
        AI가 종목 분석 리포트를 생성함
        """
        response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
                {"role": "system", "content": "너는 주식 데이터 분석 전문가야."},
                {"role": "user", "content": f"{ticker} 종목의 최근 뉴스 및 데이터를 기반으로. \
                앞으로의 주가 전망에 대해 5줄 이내 리포트써줘. 종목 코드는 말 안해도 돼. \
                글자 크기는 최대 15pt 이내로 써줘. 마지막에 이 종목을 **추천하는지 비추천하는지** 판단해서 문장 넣어줘. "}
        ]
        )
        return response.choices[0].message.content



    ticker_symbol = get_ticker_symbol(stock_name)
    #start_p = date_range[0]
    #end_p = date_range[1] + datetime.timedelta(days=1)

    # 오늘 날짜와 한 달 전 날짜 계산
    import datetime
    end_p = datetime.date.today()
    start_p = end_p - datetime.timedelta(days=30)

    # Fetch stock data
    df = fdr.DataReader(f'KRX:{ticker_symbol}', start_p, end_p)
    df.index = df.index.date

    # Display data
    st.subheader(f"최근 일주일간 {stock_name}의 주가 데이터")
    st.dataframe(df.tail(7))

    # Create plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close Price'))
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Candlestick'
                ))
    fig.update_layout(title=f'{stock_name} Stock Price',
                    xaxis_title='Date',
                    yaxis_title='Price (KRW)',
                    xaxis_rangeslider_visible=False,
                    template='plotly_dark'
                )
    st.plotly_chart(fig, use_container_width=True)


    # 데이터 표시
    if stock_name:
        # FinanceDataReader로 티커 정보 가져오기
        data = fdr.StockListing("KRX")
        #st.write(data.head())  # 데이터 확인 (디버깅용)

        if "Code" in data.columns and "Name" in data.columns:
            ticker = data[data["Name"] == stock_name]["Code"].values
            if len(ticker) > 0:
                ticker = ticker[0]

                # 재무 데이터 가져오기
                financial_data = get_financial_data(ticker)
                if "error" in financial_data:
                    st.error(f"재무 정보를 가져오는 데 실패했습니다: {financial_data['error']}")
                else:
                    # 분석 리포트 표시
                    st.subheader(f"{stock_name} AI 분석 리포트🤖")
                    reports = get_analysis_report(ticker)
                    st.write(reports)
                    
                    # 뉴스 표시
                    st.subheader(f"{stock_name}의 관련 뉴스 및 참고자료")
                    news = get_stock_news(stock_name)
                    if news:
                        for article in news:
                            st.write(f"- [{article['title']}]({article['link']})")
                    else:
                        st.write("관련 뉴스를 가져올 수 없습니다.")

            else:
                st.error("입력한 종목명을 찾을 수 없습니다.")
        else:
            st.error("데이터 구조가 예상과 다릅니다. 열 이름을 확인하세요.")
