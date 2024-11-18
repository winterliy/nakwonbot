# NAKWON CONNECT INC.
1. python으로 만든다 (단, discord.ext와 ctx는 쓰지 않는다)
2. 설정들
- 만들어야 할 파일
    - stock.json : 주식 정보 저장. {주식명 : 거래소명 : 주식코드 : 현재 한 주당 가격 : 발행된 주의 총 개수 : 거래 가능한 주식수}
    - account.json : 유저들의 통장. {유저명 : 현금보유량 : 보유주와 개수}
    - history.json : 주식들의 변동 값을 저장. {시간, 주식명, 변동된 한 주당 가격}
    - daily_reward.json : 하루에 한 번 일급을 받는데, 기록을 저장할 곳 {플레이어이름, 시간}
    - gamble_config.json : 도박 성공 확률 저장
    - lotto.json : 도박 실패시, 납세시, lotto.json에 저장.
    - lotto_player.json : 로또에 참가한 플레이어 저장.
    - tax.json : 세금을 낸 유저 리스트를 저장.
    - gamble_reward.json : 로또 보상 배율을 저장.
    - ~~company.json : 회사 리스트. {사명, 카테고리, 직원 리스트}~~
- 설정
    - 같은 주식의 모든 유저의 소유량은 발행된 주를 넘지 못함
    - $help를 치면 위의 명령어에 대한 설명을 임베드로 출력
    - 명령어를 완성하지 않거나 잘못치면 올바른 형식을 출력
    - 모든 명령어 출력은 임베트로 출력
    - 세금시스템을 만들어줘. 모든 유저에게서 하루에 한 번씩 세금을 내도록 할꺼야. 현금의 3%. 세금을 내면 tax.json에 저장. 하루가 지나도 안내면 세금 50% 부과
    - 발행된 주식중 정해진 비율 만큼은 거래되지 못한다. 한 주식에 대한 모든 유저의 소유주식의 합이 거래 가능한 주식의 수를 넘지 못한다.

3. 통장 시스템
- !계좌개설 : 계좌를 개설한다. account.json에 형식에 따라 계좌를 개설함
- !이체 <유저닉네임> <금액> : 유저에게 본인의 account.json 현금을 송금
- $account : 계좌에 대한 설정 명령어. $account 인자 형식으로 씀. (ex. $account add 유저id 금액)
    - add <유저id> <금액> : 유저에게 금액 추가
    - del <유저id> <금액> : 유저에게 금액 감소
    - set <유저id> <금액> : 유저에게 금액 정하기
- !일급 : 하루에 한 번 5만원 지급, daily_reward.json에 저장하기.
- ~~!월급 :~~
- !지갑 : 본인의 account.json를 출력. 임베드에 출력.
    - !납세 : 세금을 내는 명령어. 하루에 한 번 작동. account.json에서 현금의 3%와 보유한 주식의 20%를  lotto.json에 저장. 납세한 유저는 tax.json에 저장.ㅇ
- !로또참여 : 현금 10만원을 내고 로또에 참여. lotto_player.json에 유저 저장
- $tax : 세금에 대한 설정 명령어. $tax 인자 형식으로 씀. (ex. $tax check)
    - check : 계좌에 10만원 이상이 있는 사람 중에 tax.json에 없는 사람의 account.json에서 현금 50%와 주식의 80%를 빼서 lotto.json에 저장. 후에 tax.json을 비운다
- $lotto : 로또에 대한 설정 명령어. $lotto 인자 형식으로 씀. (ex. $lotto start)
    - start : lotto.json에 있는 돈과 주식을 lotto_player.json에 있는 유저 중 한 명을 선출하여 랜덤하게 지급. 지급 후에는 lotto_player.json을 비운다
    
4. 주식 시스템
- !매도 <거래소> <주식코드> <주> : 주만큼 주식을 매도
- !매수 <거래소> <주식코드> <주> : 주만큼 주식을 매수
- !주식목록: 임베드에 stock.json 출력.
- !주식정보 <거래소> <주식코드> : 주식에 대한 정보를 stock.json에서 추출하여 출력
- !주식기록 <거래소> <주식코드> : 주식의 한 주당 가격의 변화를 출력. history.json출력
- $stock : 주식에 대한 설정 명령어. $stock 인자 형식으로 씀. (ex.$stock publish 주식명 카테고리)
    - publish <주식명> <거래소명> <카테고리> <한 주당 가격> <발행할 주식 수> <거래 가능한 비율> : stock.json에 저장. 자동으로 주식코드 생성 (000000부터 1씩 증가)
    - delist <거래소> <주식코드> : stock.json, account.json에서 삭제, 주식 상장폐지
    - plus <거래소> <주식코드> <금액> : 주식의 한 주당 가격을 금액만큼 추가
    - minus <거래소> <주식코드> <금액> : 주식의 한 주당 가격을 금액만큼 감소
    - set <거래소> <주식코드> <금액> : 주식의 한 주딩 가격을 금액으로 정하기
    - split <거래소> <주식코드> <주> : 주식을 액면분활
    - merge <거래소> <주식코드> <주> : 주식을 액면병합
    - deal <거래소>  <주식코드> <거래 가능한 비율> : 발행된 주식 중 거래 가능한 비율을 정한다. stock.json에 저장.

5. 도박 시스템
- !bet <금액> : 도박 명령어. 금액만큼 배팅한다. 설정된 확률에 따라 성공시, gamble_reward.json에 정해진 수에 따라 배로 지급, 실패시 배팅한 금액을 lotto.json에 저장. 기본 확률은 50:50으로 저장
- $gamble : 도박에 대한 설정 명령어. $gamble 인자 형식으로 씀. (ex. $gamble probability 10)
    - probability <성공확률> : 도박의 성공확률을 정한다. gamble_config.json에 저장. 확률이 정해져 있지 않으면 50:50으로 처리.
    - reward <보상 배율> : 보상배율을 gamble_reward.json에 저장

~~6. 회사 시스템(보류)~~
- ~~!창업 <사명> <카테고리> <자본금> : company.json에 {사명, 카테고리, 자본금, 형태, }~~
- ~~!폐업 <사명> :~~
- ~~!인사 <플레이어 아이디> <직급>~~
- ~~인사, 회계, 재정, 경영, 마케팅, 서비스, 고객응대, 기업전략, 정책, 법무, 복지, 노동, 등등~~
