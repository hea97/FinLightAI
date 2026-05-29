# FinLightAI 전체 기획서

작성일: 2026-05-29  
문서 목적: FinLightAI의 서비스 방향, 핵심 기능, 웹사이트 구성, 자산 포트폴리오 기능, Discord 연동 계획을 한국어로 정리한다.

## 1. 프로젝트 한 줄 설명

FinLightAI는 AI, 반도체, 정책, 금융 뉴스와 시장 데이터를 결합해 투자자가 시장 상태와 보유 자산 리스크를 빠르게 이해하도록 돕는 금융 신호 대시보드다.

## 2. 중요한 원칙

- 이 서비스는 투자 추천 서비스가 아니다.
- `매수`, `매도`, `수익 보장` 표현을 사용하지 않는다.
- 모든 결과는 참고용 시장 상태, 뉴스 리스크, 포트폴리오 현황 정보로 제공한다.
- Discord 알림도 투자 지시가 아니라 상태 요약과 리스크 알림으로 제한한다.

## 3. 핵심 사용자

- AI/반도체/정책 뉴스가 주식시장에 주는 영향을 빠르게 보고 싶은 사용자
- 삼성전자, SK하이닉스, NVIDIA, TSMC 등 반도체 관련 종목을 추적하는 사용자
- 여러 종목을 보유하고 있고, 뉴스 리스크와 자산 비중을 함께 보고 싶은 사용자
- 웹사이트보다 Discord에서 빠르게 상태를 확인하고 싶은 사용자

## 4. 핵심 기능

### 4-1. 뉴스 기반 시장 신호

- GDELT, Guardian, Finnhub, BBC에서 뉴스를 수집한다.
- 뉴스 출처 신뢰도, 날짜 맥락, 제목 자극성, 제목-본문 일관성, 교차 보도를 확인한다.
- 신뢰도가 낮은 뉴스는 분석 파이프라인에서 차단한다.
- 신뢰 가능한 뉴스만 감성 분석과 시장 반응 분석에 사용한다.
- 최종 신호는 `RED`, `YELLOW`, `GREEN`으로 표시한다.

### 4-2. 시장 반응 분석

- 종목별 수익률, 거래량 비율, 변동성을 계산한다.
- 뉴스 발생 후 시장 반응이 과도한지 확인한다.
- 단일 뉴스만으로 강한 경고를 만들지 않고, 뉴스 신뢰도와 시장 데이터를 함께 본다.

### 4-3. 웹 대시보드

첫 화면에서 바로 보여줄 정보:

- 오늘의 전체 시장 신호
- RED/YELLOW 종목 목록
- 주요 뉴스와 신뢰도 점수
- 포트폴리오 평가금액
- 포트폴리오 일간 변동
- 자산 비중 차트
- 뉴스 리스크가 큰 보유 종목

상세 화면:

- 종목별 뉴스 타임라인
- 가격 차트
- 거래량 변화
- 뉴스 신뢰도 breakdown
- 관련 뉴스 출처 목록
- 포트폴리오 내 해당 종목 비중

### 4-4. 자산 포트폴리오 기능

사용자가 직접 보유 자산을 등록한다.

필수 입력:

- 종목 코드
- 종목명
- 보유 수량
- 평균 매입가
- 통화
- 자산 분류

계산 항목:

- 현재 평가금액
- 총 투자금
- 평가손익
- 수익률
- 전체 포트폴리오 내 비중
- 섹터별 비중
- 통화별 비중
- RED/YELLOW 뉴스 노출 비중

주의:

- 실제 증권 계좌 자동 연동은 후순위다.
- MVP에서는 사용자가 직접 입력한 포트폴리오로 시작한다.
- 계좌 연동은 보안, 인증, 개인정보 처리 정책이 준비된 뒤 진행한다.

### 4-5. Discord 연동

Discord는 빠른 조회와 알림 채널로 사용한다.

명령어 후보:

```text
!상태
!뉴스
!신호
!자산
!자산 삼성전자
!리스크
```

`!자산` 응답 예시:

```text
FinLightAI 자산 요약

총 평가금액: 12,450,000 KRW
일간 변동: -1.24%
평가손익: +840,000 KRW (+7.24%)

상위 보유 자산
1. 삼성전자 42.1% | YELLOW | 뉴스 신뢰도 0.88
2. NVIDIA 31.4% | GREEN | 뉴스 신뢰도 0.81
3. SK하이닉스 18.9% | YELLOW | 뉴스 신뢰도 0.84

리스크 메모
- 반도체 정책 뉴스로 YELLOW 신호 2건 발생
- 단일 출처 뉴스는 신호 계산에서 제외됨

주의: 이 내용은 투자 추천이 아닙니다.
```

자동 알림 조건:

- 보유 비중 20% 이상 종목에서 RED 신호 발생
- 포트폴리오 전체 평가금액 일간 변동률이 임계값 초과
- 특정 종목 뉴스 신뢰도 0.85 이상이며 YELLOW/RED 발생
- 단일 섹터 비중이 60% 이상이고 해당 섹터에 RED 뉴스 발생

## 5. 화면 기획

### 메인 대시보드

- 전체 신호 카드
- 포트폴리오 요약
- 주요 보유 종목 리스크
- 최신 신뢰 뉴스
- 차단된 의심 뉴스 수

### 포트폴리오 페이지

- 자산 목록 테이블
- 종목 추가/수정/삭제
- 평가금액과 수익률
- 자산 비중 차트
- 섹터/통화 분산 차트
- 보유 종목별 뉴스 신호

### 뉴스 검증 페이지

- 수집 뉴스 목록
- 신뢰도 점수
- 차단 사유
- 출처별 점수
- 교차 보도 여부

### Discord 설정 페이지

- Webhook URL 설정 상태
- 알림 채널 테스트
- 알림 조건 설정
- 명령어 사용 안내

## 6. 개발 단계

### Phase 1: 뉴스 신호 MVP

- GDELT collector 구현
- Guardian collector 구현
- Finnhub news collector 구현
- BBC RSS collector 구현
- 가짜뉴스 필터와 신호 생성 연결
- Discord RED/YELLOW 알림 검증

### Phase 2: 포트폴리오 MVP

- 포트폴리오 DB 테이블 추가
- 자산 CRUD API 구현
- yfinance/pykrx 가격 업데이트
- 포트폴리오 평가금액 계산
- 웹 대시보드에 포트폴리오 카드 추가

### Phase 3: Discord 자산 명령

- Discord bot command handler 추가
- `!자산` 명령 구현
- `!자산 종목명` 상세 조회 구현
- Discord 응답 텍스트 formatter 구현

### Phase 4: 리스크 알림 고도화

- 보유 비중 기반 알림
- 섹터 집중도 알림
- 포트폴리오 변동률 알림
- 뉴스 신뢰도 기반 알림

### Phase 5: 모델 고도화

- KoFinBERT/FinBERT 감성 분석 연결
- 이벤트 점수 모델 개선
- 백테스트 리포트 추가

## 7. DB 테이블 초안

```text
users
portfolio_accounts
portfolio_positions
portfolio_snapshots
market_prices
news_articles
news_filter_results
market_signals
discord_channels
discord_commands
asset_alert_rules
```

## 8. API 엔드포인트 초안

```text
GET    /api/signals
GET    /api/news
GET    /api/market
GET    /api/portfolio
POST   /api/portfolio/positions
PATCH  /api/portfolio/positions/{id}
DELETE /api/portfolio/positions/{id}
GET    /api/portfolio/risk
POST   /api/discord/test
POST   /api/discord/commands/asset-summary
```

## 9. 당장 추가할 TODO

- [ ] 뉴스 API 관리 설정 파일 추가
- [ ] GDELT collector 구현
- [ ] Guardian collector 구현
- [ ] Finnhub collector 구현
- [ ] BBC RSS collector 구현
- [ ] 포트폴리오 position schema 설계
- [ ] 포트폴리오 CRUD API 설계
- [ ] `!자산` Discord 응답 formatter 구현
- [ ] 웹 대시보드에 포트폴리오 요약 카드 추가
- [ ] 투자 추천이 아님을 모든 화면과 Discord 응답에 표시
