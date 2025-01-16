# 스마트 트레이딩: AI 주식 분석 및 예측


## 📝 프로젝트 소개
이 프로젝트는 Streamlit을 활용하여 주식 데이터 조회, 거래, 시각화, 그리고 AI 기반 종목 분석 기능을 제공하는 스마트 트레이딩 시스템 웹 애플리케이션입니다.

사용자는 개인 금융 데이터를 관리하고, 주식 포트폴리오를 시뮬레이션하며, AI의 도움을 받아 종목 분석 및 미래 주가 예측 결과를 확인할 수 있습니다. 

본 프로젝트는 4명의 조원이 협력하여 제작하였습니다.

## 📂 주요 기능
### 1️⃣ 마이페이지
- 설명: 사용자의 금융 데이터를 종합적으로 관리하고 시각화하는 기능을 제공합니다.
- 주요 기능:
  - 사용자 정보 및 총 자산 현황 표시
  - 보유 주식의 상세 정보와 종목별 자산 비중 파이 차트 제공
  - 기간별 자산 변동 데이터를 기반으로 누적 자산 변동 그래프 생성

### 2️⃣ 주식 거래 페이지
- 설명: 사용자가 주식 종목을 검색하고 매수 및 매도 시뮬레이션을 수행할 수 있는 기능을 제공합니다.
- 주요 기능: 회사 이름으로 주식 검색 및 선택
- 주식 매수:
  - 현재 주가 조회 및 한 달 간의 주가 변동 차트 제공
  - 매수 수량 입력 후 자산 상태에 따른 결과 표시
- 주식 매도:
  - 매도 날짜 입력 및 LSTM 기반 주가 예측
  - 과거 데이터와 예측 데이터를 비교한 캔들 차트 및 예측 종가 라인 그래프 제공

- LSTM 모델 구조
![1](https://github.com/user-attachments/assets/2e82ffa0-dbcc-4230-980a-625f168b6c07)



- 학습 데이터
  2015년 부터 삼성전자 종가 데이터
![2](https://github.com/user-attachments/assets/8cd21923-a98d-4221-b232-d058e520c051)




### 3️⃣ 차트 검색 페이지
- 설명: 원하는 종목의 과거 주가 데이터를 시각화하고, LSTM 딥러닝 모델을 활용하여 미래 주가를 예측합니다.

- 주요 기능:
  - 회사 이름으로 종목 검색 및 기간 선택
  - 과거 주가 데이터를 테이블 및 캔들 차트로 시각화
  - LSTM 모델을 사용하여 미래 주가 예측값 제공 및 시각화

### 4️⃣ AI 종목 분석 페이지
- 설명: AI를 통해 사용자가 입력한 종목에 대한 분석 리포트를 생성하고 관련 뉴스를 제공하는 기능을 제공합니다.

- 주요 기능:
  - 회사 이름으로 종목 검색 및 최근 한 달간 주가 데이터를 캔들 차트로 시각화
  - OpenAI GPT 모델을 활용한 AI 분석 리포트 생성 (추천 여부 포함)
  - 네이버 뉴스에서 종목 관련 최신 기사 크롤링 및 링크 제공


## 📊 구현 화면

### 회원가입 페이지
![회원가입](https://github.com/user-attachments/assets/16b24ba7-0430-4348-ac25-b416e7716e20)

- 이름과 보유자산을 입력하여 회원가입
- 로그인 후에는 네이버 금융 주요뉴스를 표시.

### 마이페이지

![마이페이지_1](https://github.com/user-attachments/assets/410a1528-49c2-44b1-8a21-91b2d9ccfb4a)

- 현재 자산 상황: 사용자 이름, 총 자산, 현금 자산을 표시.
- 보유 종목 요약: 보유 중인 주식의 상세 정보를 테이블로 표시.
- 종목 비중 파이 차트: 포트폴리오 내 현금과 보유 주식의 비중을 시각화.
- 누적 자산 변동 그래프: 기간별 누적 자산의 변동 추세를 시각화.

![마이페이지_2](https://github.com/user-attachments/assets/9327ce17-9c17-4e22-849e-9ff016aac4d8)

- 총 투자 수익률: 미래 날짜에 매도 예약을 걸 수 있음. 모델이 예측한 종가 가격으로 투자 수익률을 계산해 마이페이지에 표시.


### 주식 거래 페이지
![주식 매수](https://github.com/user-attachments/assets/af602a6b-93f6-4241-acbf-40e4e5129e21)

- 주식 매수:
  - 검색한 종목의 일주일 주가 예측값과 한 달간의 주가 데이터를 차트로 제공.
  - 매수 버튼 클릭 시 결과 메시지 출력.

![주식 매도 오류](https://github.com/user-attachments/assets/2cdf0143-1466-4d58-b094-01f80dd38d81)

- 주식 매도:
  - LSTM 모델로 매도 날짜의 주가 예측값 시각화.
  - 캔들 차트와 예측 종가 라인 그래프 제공.
  - 보유 개수보다 많은 양을 매도 시, 오류 메시지 출력.

### 차트 검색 페이지
![차트](https://github.com/user-attachments/assets/eea37969-1c58-4954-a5d2-5b582873e460)


- 종목 검색 및 데이터 시각화:
  - 입력된 기간 동안 주가 데이터를 캔들 차트와 테이블로 표시.
  - 미래 주가 예측 결과를 빨간 점선 그래프로 표시.

### AI 종목 분석 페이지

![Animation](https://github.com/user-attachments/assets/149a4139-8d45-4a50-8a23-b9ed161abeee)

- AI 분석 리포트:
  - OpenAI GPT 모델이 생성한 간단한 종목 분석 리포트 제공.
  - 리포트에는 종목 추천 여부 포함.
- 관련 뉴스 크롤링:
  - 네이버 뉴스에서 해당 종목의 최신 기사 크롤링 및 링크 제공.

## 👩‍💻 조원 소개
- 조원 1: 오세현
- 조원 2: 윤웅상
- 조원 3: 이승연
- 조원 4: 이재영
---------------------------------------------
## 📜 기술 스택
- 프로그래밍 언어: Python

- 웹 프레임워크: Streamlit

- 데이터 분석:
Pandas
FinanceDataReader (주식 데이터 수집)

- 머신러닝:
TensorFlow (LSTM 기반 주가 예측 모델)
OpenAI GPT (AI 기반 종목 분석)
Scikit-learn (데이터 스케일링)

- 시각화:
Plotly (라인 차트, 파이 차트, 캔들 차트)

- 웹 크롤링:
BeautifulSoup (네이버 뉴스 크롤링)

## 👿 Troubleshooting
‼️ LSTM 모델 학습 및 사용 시 입력데이터 출력 데이터의 차원을 관리하는 것이 어려웠다.
  
  ✅ 데이터 data type과 shape를 확인하고 reshape 과정을 거쳐 전처리 하였다.


‼️ Open AI api 키를 코드에 직접 넣어 사용하다 보안상의 문제로 .env파일에 넣어 이용하였다. 변경 후 환경변수를 읽어오고 client 객체를 생성하는데 이전에는 발생하지 않던 오류가 발생하였다.
  
  ✅ 사용자가 직접 api키를 입력하여 이용하는 방식으로 변경하였다.


‼️ 사용자 클래스를 생성하고 streamlit session state에 넣어 자산 변경사항을 저장하였다. 거래 시 다양한 자료형에서 가격 데이터를 참조하는데 인덱싱하고 자료형을 통일하는 것에 어려움을 겪었다.
  
  ✅ 지속적으로 디버깅하며 올바른 데이터를 가져오는지 확인하고 필요한 경우 형변환을 하였다. 이 때 원본이 손상되지 않도록 주의하였다.


‼️ 배포할 때 로컬 환경과 python 버전이 달라서 패키지 충돌이 일어났다.
  
  ✅ 고급 환경설정을 통해 Python 3.11 버전으로 변경하여 배포하였다.
  

## Streamlit URL
[Streamlit URL](https://smart-treding-stock.streamlit.app/)

## 📌 참고 자료
[Streamlit 공식 문서](https://docs.streamlit.io/)
[FinanceDataReader GitHub](https://github.com/FinanceData/FinanceDataReader)
[TensorFlow 공식 문서](https://www.tensorflow.org/?hl=ko)
[OpenAI API 문서](https://platform.openai.com/docs/overview)
[Plotly 공식 문서](https://plotly.com/python/)
[KRX 상장 종목 정보](https://kind.krx.co.kr/main.do?method=loadInitPage&scrnmode=1)
[BeautifulSoup 공식 문서](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
