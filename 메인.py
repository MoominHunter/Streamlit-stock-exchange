import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
import datetime
import matplotlib.pyplot as plt
import matplotlib 
from io import BytesIO
import plotly.graph_objects as go
import pandas as pd
from bs4 import BeautifulSoup
import requests

#종목 클래스 정의 
class Stock:
    def __init__(self, name, purchase_price, count):
        self.name = name                    # 종목명
        self.purchase_price = purchase_price  # 구매 당시 가격
        self.count = count            # 보유 주식 수
    def total_value(self): #자산
        return self.purchase_price * self.count
    

# User 클래스 정의
class User:
    def __init__(self, name, money):
        self.name = name
        self.money = money
        self.stocks = []

    def add_stock(self, stock_name, purchase_price, count):
        new_stock = Stock(stock_name, purchase_price, count)
        self.stocks.append(new_stock)

    def total_asset(self):
        """총 자산 계산 (보유 종목 포함)"""
        stock_value = sum(stock.total_value() for stock in self.stocks)
        return self.money + stock_value

    def list_stocks(self):
        """보유 종목 출력"""
        return [stock.name for stock in self.stocks]
    
    def buy_stock(self,stock_name,stock_price,stock_count):
        total_cost = stock_price * stock_count
        if self.money < total_cost:
            return f"잔액 부족: 현재 잔액은 {self.money:,}원입니다."
        for stock in self.stocks:
            if stock.name == stock_name:
                stock.count += stock_count
                self.money -= total_cost
                return f"{stock_name} 종목을 {stock_count}개 매수하였습니다."
        new_stock = Stock(stock_name, stock_price, stock_count)
        self.stocks.append(new_stock)
        self.money -= total_cost
        return f"{stock_name} 종목이 새로 {stock_count}개 추가되었습니다."
    
    def sell_stock(self, stock_name, stock_price, stock_count):
        total_income = stock_price * stock_count
        for stock in self.stocks:
            if stock.name == stock_name:
                # 보유량보다 많은 주식을 매도하려는 경우
                if stock_count > stock.count:
                    return f"현재 {self.name}님의 {stock_name} 보유량은 {stock.count}개입니다. 매도할 수 없습니다."
                # 정상 매도
                stock.count -= stock_count
                self.money += total_income
                # 보유량이 0이 되면 종목 제거
                if stock.count == 0:
                    self.stocks.remove(stock)
                return f"{stock_name} 종목을 {stock_count}개 매도하였습니다. 총 {total_income:,}원이 입금되었습니다."
            
        return f"{self.name}님은 {stock_name}을 보유하고 있지 않습니다."

def get_stock_news():
    """
    네이버 금융 뉴스 페이지에서 주요 뉴스 크롤링
    """
    base_url = "https://finance.naver.com/news/"
    response = requests.get(base_url)
    
    # 요청 실패 처리
    if response.status_code != 200:
        raise Exception(f"Failed to fetch the page: {response.status_code}")

    # HTML 파싱
    soup = BeautifulSoup(response.text, "html.parser")

    # 뉴스 섹션 선택
    news_section = soup.find("div", {"class": "main_news"})
    
    # 뉴스 기사 정보 추출
    articles = []
    if news_section:
        for item in news_section.find_all("li"):
            link_tag = item.find("a")
            if link_tag:
                title = link_tag.get_text(strip=True)
                link = link_tag["href"]
                articles.append({"title": title, "link": base_url + link[5:]})
                
    else:
        raise Exception("News section not found on the page.")

    return articles

# 테스트 실행
if __name__ == "__main__":
    try:
        news = get_stock_news()
        for idx, article in enumerate(news, start=1):
            print(f"{idx}. {article['title']}\n   Link: {article['link']}\n")
    except Exception as e:
        print(f"Error: {e}")
    
# Session State 초기화
if "user1" not in st.session_state or st.session_state.user1 is None:
    st.session_state.user1 = None  # 초기값은 None
    # 사용자 입력
    st.title("회원 가입")
    user_name = st.text_input("이름", value="", key="name_input")
    user_money = st.text_input("보유 자산", value="0", key="money_input")

    # 사용자 객체 생성 및 저장
    if st.button("회원 가입"):

        if st.session_state.user1:
            st.warning("이미 생성된 계정입니다.")  # 이미 계정이 있는 경우 경고 메시지 표시
        else:
            try:
                user_money = int(user_money)  # 숫자로 변환 시도
                st.session_state.user1 = User(user_name, user_money)  # 사용자 객체 저장
                st.success(f"사용자 {user_name}이 생성되었습니다! 보유 자산: {user_money:,}원")
            except ValueError:
                st.error("숫자로 입력해주세요.")  # 숫자로 변환 실패 시 오류 메시지 표시
else:
    if st.session_state.user1 is not None:
        st.title(f"{st.session_state.user1.name}님 환영합니다.")
        news = get_stock_news()
        if news:
            st.markdown("### TODAY NEWS")
            for article in news:
                st.write(f"- [{article['title']}]({article['link']})")
            
        else:
            st.write("관련 뉴스를 가져올 수 없습니다.")
