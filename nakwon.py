# import datetime
import json
import os
# from discord.ext import commands
# from random import choice
# from random import randint
# import yt_dlp as youtube_dl
from datetime import datetime
from http import client
import discord
# import sys
# from discord.sinks import WaveSink

now = datetime.now()
today = now.date()

intents = discord.Intents.default()
intents.message_content = True
intents.typing = False
intents.presences = False
intents.reactions = True
intents.guilds = True
intents.voice_states = True
intents.members = True

folder = 'file_folder'
FOLDER = "economics"
account_file = 'account.json'
FILES = {
    "stock.json": {},
    "account.json": {},
    "history.json": [],
    "daily_reward.json": [],
    "gamble_config.json": {"probability": 50},
    "lotto.json": {"cash": 0, "stocks": {}},
    "lotto_player.json": [],
    "tax.json": [],
    "gamble_reward.json": {"multiplier": 2},
}
ACCOUNT_FILE = 'economics/account.json'
STOCK_FILE = 'economics/stock.json'
TAX_PERSON_FILE = "economics/tax_person.json"

# 폴더 및 파일 생성
if not os.path.exists(FOLDER):
    os.mkdir(FOLDER)

for file, initial_data in FILES.items():
    path = os.path.join(FOLDER, file)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(initial_data, f, indent=4, ensure_ascii=False)

fortunes = [
    "오늘은 모든 일이 잘 풀릴 것입니다! 행운이 따르세요.",
    "작은 성공이 있을 것입니다. 하지만 큰 도전은 피하세요.",
    "조금 더 기다리면 더 좋은 일이 생길 것입니다. 인내가 필요해요.",
    "운이 다소 부족할 수 있습니다. 신중하게 결정하세요.",
    "오늘은 사람들과의 관계에서 운이 따를 것입니다. 좋은 소식이 있을 거예요.",
    "조금 더 노력하면 큰 성과를 거둘 수 있을 것입니다. 포기하지 마세요.",
    "당신의 운세는 그다지 좋지 않습니다. 조심스럽게 행동하세요.",
    "새로운 기회가 올 수 있습니다. 과감히 도전해보세요!"
]

compatibilities = [
    "두 사람은 정말 잘 맞는 궁합입니다! 함께라면 모든 일이 잘 풀릴 거예요.",
    "상당히 좋은 궁합이에요. 다소 의견 차이가 있을 수 있지만 서로 보완할 수 있을 거예요.",
    "음... 조금 불안정한 궁합이네요. 갈등이 생길 수도 있으니 조심하세요.",
    "두 사람은 맞지 않는 궁합이에요. 의견 충돌이 많을 수 있으니 신중하세요.",
    "서로를 잘 이해하는 궁합이에요. 어떤 상황에서도 함께 잘 해결할 수 있을 것입니다.",
    "좋지 않은 궁합이에요. 갈등이 생길 수 있으니 주의가 필요합니다."
]

근로소득세 = 0.001
복권세금 = 0.001
도박세금 = 0.01
매수세금 = 0.001
매도세금 = 0.001
이체세금 = 0.01
납세율 = 0.003
탈세벌금 = 0.8
주식탈세벌금 = 0.8
주식최소금액 = 100
주식확률 = 0.65

def stock_random():
    import random
    from datetime import datetime

    stock_path = os.path.join(FOLDER, "stock.json")
    history_path = os.path.join(FOLDER, "history.json")

    try:
        # stock.json 읽기
        with open(stock_path, "r", encoding="utf-8") as f:
            stock_data = json.load(f)

        if not stock_data:
            print("등록된 주식이 없습니다.")
            return

        # history.json 읽기 (없으면 초기화)
        if not os.path.exists(history_path):
            with open(history_path, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4, ensure_ascii=False)

        with open(history_path, "r", encoding="utf-8") as f:
            history_data = json.load(f)

        # 모든 주식의 가격 랜덤 변경
        for stock_key, stock_info in stock_data.items():
            # 기존 가격 가져오기
            current_price = stock_info.get("price", 100)

            # 상승/하락 비율 설정 (상승 확률 60%, 하락 확률 50%)
            if random.random() < 주식확률:  # 60% 확률로 상승
                random_factor = random.uniform(1.01, 1.2)  # +1% ~ +20%
            else:  # 40% 확률로 하락
                random_factor = random.uniform(0.9, 0.99)  # -1% ~ -10%

            new_price = max(주식최소금액, int(current_price * random_factor))  # 가격은 최소 1원 이상

            # 주식 정보 업데이트
            stock_info["price"] = new_price

            # history.json에 변경 기록 추가
            history_entry = {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "exchange": stock_info.get("exchange", "Unknown"),  # 거래소 정보
                "code": stock_info.get("code", "Unknown"),  # 주식 코드
                "name": stock_key,  # 주식명 (키 값)
                "price": new_price  # 한 주당 주가
            }
            history_data.append(history_entry)

        # stock.json 업데이트
        with open(stock_path, "w", encoding="utf-8") as f:
            json.dump(stock_data, f, indent=4, ensure_ascii=False)

        # history.json 업데이트
        with open(history_path, "w", encoding="utf-8") as f:
            json.dump(history_data, f, indent=4, ensure_ascii=False)

        print("모든 주식의 가격이 랜덤하게 변경되고, 변경 이력이 저장되었습니다!")

    except Exception as e:
        print(f"주식 가격 변경 중 오류가 발생했습니다: {e}")

def int_changer():
    try:
        # JSON 파일 읽기
        with open('economics/account.json', "r", encoding="utf-8") as f:
            account_data = json.load(f)

        # 데이터 변환
        for user_id, account_info in account_data.items():
            # cash 값을 정수로 변환
            account_info["cash"] = int(account_info["cash"])

            # stocks 값을 정수로 변환
            account_info["stocks"] = {stock: int(quantity) for stock, quantity in account_info["stocks"].items()}

        # 변환된 데이터 저장
        with open('economics/account.json', "w", encoding="utf-8") as f:
            json.dump(account_data, f, indent=4, ensure_ascii=False)

        print("account.json 파일의 cash와 stocks 값을 성공적으로 정수로 변환했습니다!")

    except Exception as e:
        print(f"오류가 발생했습니다: {e}")

client = discord.Client(intents=intents)

@client.event
async def save_image(attachment):
    if not os.path.exists(folder):
        os.makedirs(folder)

    now = datetime.now()
    time = f"{str(now.year)}년 {str(now.month)}월 {str(now.day)}일 {str(now.hour)}시 {str(now.minute)}분 {str(now.second)}초"

    image_url = attachment.url
    image_name = attachment.filename
    image_path = os.path.join(folder, image_name)

    await attachment.save(image_path)
    f = (open('log.txt', 'a'))
    f.write(f"Saved file: {image_name} at {image_path} in {time}" + '\n')
    f.close()

class MyClient(discord.Client):
    @client.event
    async def on_ready(self):
        await client.change_presence(status=discord.Status.online)
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="우리소리골"))

    async def on_message(self, message, random=None):
        global 주식확률  # 전역 변수 선언
        global 근로소득세
        global 복권세금
        global 도박세금
        global 매수세금
        global 매도세금
        global 이체세금
        global 납세율
        global 탈세벌금
        global 주식탈세벌금
        global 주식최소금액

        if message.author.bot:
            return None

        content = message.content.strip()

        if message.content.startswith("$세율설정"):
            args = message.content.split()
            if len(args) != 3:
                await message.channel.send(
                    "올바른 형식: `$세율설정 <세금 이름> <값>`\n"
                    "설정 가능한 세금: 근로소득세, 복권세금, 도박세금, 매수세금, 매도세금, "
                    "이체세금, 납세율, 탈세벌금, 주식탈세벌금, 주식최소금액"
                )
                return

            tax_name = args[1]
            try:
                value = float(args[2])
                if value < 0:
                    await message.channel.send("세금 값은 0 이상의 값이어야 합니다.")
                    return

                if tax_name == "근로소득세":
                    근로소득세 = value
                elif tax_name == "복권세금":
                    복권세금 = value
                elif tax_name == "도박세금":
                    도박세금 = value
                elif tax_name == "매수세금":
                    매수세금 = value
                elif tax_name == "매도세금":
                    매도세금 = value
                elif tax_name == "이체세금":
                    이체세금 = value
                elif tax_name == "납세율":
                    납세율 = value
                elif tax_name == "탈세벌금":
                    탈세벌금 = value
                elif tax_name == "주식탈세벌금":
                    주식탈세벌금 = value
                elif tax_name == "주식최소금액":
                    주식최소금액 = value
                else:
                    await message.channel.send("올바른 세금 이름을 입력하세요.")
                    return

                await message.channel.send(f"{tax_name}이(가) {value}로 설정되었습니다.")

            except ValueError:
                await message.channel.send("값은 숫자여야 합니다.")

        if message.content == "!세율":
            await message.channel.send(
                f"**현재 세금 설정:**\n"
                f"근로소득세: {근로소득세}\n"
                f"복권세금: {복권세금}\n"
                f"도박세금: {도박세금}\n"
                f"매수세금: {매수세금}\n"
                f"매도세금: {매도세금}\n"
                f"이체세금: {이체세금}\n"
                f"납세율: {납세율}\n"
                f"탈세벌금: {탈세벌금}\n"
                f"주식탈세벌금: {주식탈세벌금}\n"
                f"주식최소금액: {주식최소금액}"
            )

        # '!set_probability <값>' 명령어 처리
        if message.content.startswith("$주식등락률설정"):
            try:
                args = message.content.split()
                if len(args) != 2:
                    await message.channel.send("올바른 형식: `$주식등락률설정 <0~1 사이 값>`")
                    return

                value = float(args[1])
                if 0 <= value <= 1:
                    주식확률 = value
                    await message.channel.send(f"주식 확률이 {주식확률}로 설정되었습니다.")
                else:
                    await message.channel.send("확률 값은 0과 1 사이의 소수여야 합니다.")
            except ValueError:
                await message.channel.send("확률 값은 숫자여야 합니다.")

        # '!get_probability' 명령어 처리
        if message.content == "$주식등락률보기":
            await message.channel.send(f"현재 주식 확률은 {주식확률}입니다.")

        if message.content.startswith("!계좌개설"):
            user_id = str(message.author.id)
            path = os.path.join(FOLDER, "account.json")

            with open(path, "r+", encoding="utf-8") as f:
                data = json.load(f)
                if user_id in data:
                    await message.channel.send("이미 계좌가 존재합니다.")
                    return
                data[user_id] = {"cash": 0, "stocks": {}}
                f.seek(0)
                json.dump(data, f, indent=4, ensure_ascii=False)

            await message.channel.send("계좌가 성공적으로 개설되었습니다.")

        if message.content.startswith("!일급"):
            user_id = str(message.author.id)
            reward = 50000
            daily_path = os.path.join(FOLDER, "daily_reward.json")
            account_path = os.path.join(FOLDER, "account.json")

            with open(daily_path, "r+", encoding="utf-8") as f:
                daily_data = json.load(f)
                import datetime
                today = datetime.datetime.now().strftime("%Y-%m-%d")

                if any(record["user"] == user_id and record["date"] == today for record in daily_data):
                    await message.channel.send("이미 오늘의 일급을 받았습니다.")
                    return

                daily_data.append({"user": user_id, "date": today})
                f.seek(0)
                json.dump(daily_data, f, indent=4, ensure_ascii=False)

            with open(account_path, "r+", encoding="utf-8") as f:
                account_data = json.load(f)
                if user_id not in account_data:
                    await message.channel.send("계좌를 먼저 개설해주세요.")
                    return

                account_data[user_id]["cash"] += reward
                f.seek(0)
                json.dump(account_data, f, indent=4, ensure_ascii=False)

            await message.channel.send(f"{reward}원이 지급되었습니다.")

            user_id = str(message.author.id)  # 유저 ID 가져오기

            # tax_person.json 파일 확인
            if os.path.exists(TAX_PERSON_FILE):
                with open(TAX_PERSON_FILE, 'r', encoding="utf-8") as f:
                    tax_person_data = json.load(f)
            else:
                tax_person_data = {}

            import datetime
            today_date = datetime.datetime.now().strftime("%Y-%m-%d")  # 오늘 날짜

            # 납세 처리: 현금과 주식 확인 및 납세 진행
            account_path = os.path.join(FOLDER, "account.json")
            with open(account_path, "r", encoding="utf-8") as f:
                account_data = json.load(f)

            if user_id not in account_data:
                await message.channel.send("계좌가 존재하지 않습니다. 계좌를 개설해주세요.")
            else:
                user_account = account_data[user_id]
                cash_balance = user_account["cash"]

                tax_amount = cash_balance * 근로소득세  # 소득세 10% 세금

                # 현금 차감
                user_account["cash"] -= tax_amount

                # 로또 기금에 세금 금액 추가
                lotto_path = os.path.join(FOLDER, "lotto.json")
                if not os.path.exists(lotto_path):
                    # 로또 파일이 없으면 기본값을 설정하여 생성
                    lotto_data = {"cash": 0, "stocks": {}}
                else:
                    try:
                        with open(lotto_path, "r", encoding="utf-8") as f:
                            lotto_data = json.load(f)
                    except json.JSONDecodeError:
                        # JSON 오류가 발생하면 기본값으로 초기화
                        lotto_data = {"cash": 0, "stocks": {}}

                lotto_data["cash"] += tax_amount  # 세금 금액을 로또 기금에 추가

                # 로또 파일에 업데이트된 데이터 저장
                with open(lotto_path, "w", encoding="utf-8") as f:
                    json.dump(lotto_data, f, indent=4, ensure_ascii=False)

                # 계좌 정보 업데이트: 차감된 현금과 주식 정보 저장
                with open(account_path, "w", encoding="utf-8") as f:
                    json.dump(account_data, f, ensure_ascii=False, indent=4)

        if message.content.startswith("!납세"):
            user_id = str(message.author.id)  # 유저 ID 가져오기

            # tax_person.json 파일 확인
            if os.path.exists(TAX_PERSON_FILE):
                with open(TAX_PERSON_FILE, 'r', encoding="utf-8") as f:
                    tax_person_data = json.load(f)
            else:
                tax_person_data = {}

            import datetime
            today_date = datetime.datetime.now().strftime("%Y-%m-%d")  # 오늘 날짜

            # 이미 납세한 경우
            if user_id in tax_person_data and tax_person_data[user_id] == today_date:
                await message.channel.send("오늘은 이미 납세를 하셨습니다. 내일 다시 시도해 주세요.")
            else:
                # 납세 처리: 현금과 주식 확인 및 납세 진행
                account_path = os.path.join(FOLDER, "account.json")
                with open(account_path, "r", encoding="utf-8") as f:
                    account_data = json.load(f)

                if user_id not in account_data:
                    await message.channel.send("계좌가 존재하지 않습니다. 계좌를 개설해주세요.")
                else:
                    user_account = account_data[user_id]
                    cash_balance = user_account["cash"]
                    stock_balance = user_account["stocks"]

                    tax_amount = cash_balance * 납세율  # 3% 세금

                    # 현금이 부족하면 납세할 수 없음
                    if cash_balance < tax_amount:
                        await message.channel.send("납세를 위한 현금이 부족합니다.")
                    else:
                        # 현금 차감
                        user_account["cash"] -= tax_amount

                        # 로또 기금에 세금 금액 추가
                        lotto_path = os.path.join(FOLDER, "lotto.json")
                        if not os.path.exists(lotto_path):
                            # 로또 파일이 없으면 기본값을 설정하여 생성
                            lotto_data = {"cash": 0, "stocks": {}}
                        else:
                            try:
                                with open(lotto_path, "r", encoding="utf-8") as f:
                                    lotto_data = json.load(f)
                            except json.JSONDecodeError:
                                # JSON 오류가 발생하면 기본값으로 초기화
                                lotto_data = {"cash": 0, "stocks": {}}

                        lotto_data["cash"] += tax_amount  # 세금 금액을 로또 기금에 추가

                        # 로또 파일에 업데이트된 데이터 저장
                        with open(lotto_path, "w", encoding="utf-8") as f:
                            json.dump(lotto_data, f, indent=4, ensure_ascii=False)

                        # 계좌 정보 업데이트: 차감된 현금 저장
                        with open(account_path, "w", encoding="utf-8") as f:
                            json.dump(account_data, f, ensure_ascii=False, indent=4)

                        # 납세 기록 추가
                        tax_person_data[user_id] = today_date
                        with open(TAX_PERSON_FILE, 'w', encoding="utf-8") as f:
                            json.dump(tax_person_data, f, ensure_ascii=False, indent=4)

                        await message.channel.send(f"납세가 완료되었습니다. {tax_amount} 원이 차감되었습니다.")

        if message.content.startswith("!기부"):
            args = message.content.split()
            if len(args) != 2 or not args[1].isdigit():
                await message.channel.send("올바른 형식: `!기부 <금액>`")
                return

            donation_amount = int(args[1])
            user_id = str(message.author.id)
            account_path = os.path.join(FOLDER, "account.json")
            lotto_path = os.path.join(FOLDER, "lotto.json")

            try:
                # account.json 파일 읽기
                with open(account_path, "r+", encoding="utf-8") as f:
                    account_data = json.load(f)

                    # 계좌 확인
                    if user_id not in account_data:
                        await message.channel.send("계좌를 먼저 개설해주세요.")
                        return

                    # 보유 금액 확인
                    if account_data[user_id]["cash"] < donation_amount:
                        await message.channel.send("보유 현금이 부족합니다.")
                        return

                    # 금액 차감
                    account_data[user_id]["cash"] -= donation_amount
                    f.seek(0)
                    json.dump(account_data, f, indent=4, ensure_ascii=False)
                    f.truncate()

                # lotto.json 파일 읽기 및 업데이트
                with open(lotto_path, "r+", encoding="utf-8") as f:
                    lotto_data = json.load(f)

                    # 기부금 추가
                    lotto_data["cash"] += donation_amount
                    f.seek(0)
                    json.dump(lotto_data, f, indent=4, ensure_ascii=False)
                    f.truncate()

                # 완료 메시지
                await message.channel.send(f"{donation_amount}원이 성공적으로 기부되었습니다!")

            except Exception as e:
                await message.channel.send(f"기부 처리 중 오류가 발생했습니다: {e}")

        if message.content.startswith("!로또참여"):
            user_id = str(message.author.id)
            account_path = os.path.join(FOLDER, "account.json")
            lotto_player_path = os.path.join(FOLDER, "lotto_player.json")

            with open(account_path, "r+", encoding="utf-8") as f:
                account_data = json.load(f)
                if user_id not in account_data:
                    await message.channel.send("계좌를 먼저 개설해주세요.")
                    return

                if account_data[user_id]["cash"] < 100000:
                    await message.channel.send("로또에 참가하려면 최소 10만 원의 현금이 필요합니다.")
                    return

                account_data[user_id]["cash"] -= 100000
                f.seek(0)
                json.dump(account_data, f, indent=4, ensure_ascii=False)

            with open(lotto_player_path, "r+", encoding="utf-8") as f:
                lotto_players = json.load(f)
                if user_id in lotto_players:
                    await message.channel.send("이미 로또에 참가하셨습니다.")
                    return

                lotto_players.append(user_id)
                f.seek(0)
                json.dump(lotto_players, f, indent=4, ensure_ascii=False)

            await message.channel.send("로또에 참가하였습니다. 행운을 빕니다!")

            user_id = str(message.author.id)  # 유저 ID 가져오기

            # tax_person.json 파일 확인
            if os.path.exists(TAX_PERSON_FILE):
                with open(TAX_PERSON_FILE, 'r', encoding="utf-8") as f:
                    tax_person_data = json.load(f)
            else:
                tax_person_data = {}

            import datetime
            today_date = datetime.datetime.now().strftime("%Y-%m-%d")  # 오늘 날짜

            # 납세 처리: 현금과 주식 확인 및 납세 진행
            account_path = os.path.join(FOLDER, "account.json")
            with open(account_path, "r", encoding="utf-8") as f:
                account_data = json.load(f)

            if user_id not in account_data:
                await message.channel.send("계좌가 존재하지 않습니다. 계좌를 개설해주세요.")
            else:
                user_account = account_data[user_id]
                cash_balance = user_account["cash"]

                tax_amount = cash_balance * 복권세금  # 소득세 10% 세금

                # 현금 차감
                user_account["cash"] -= tax_amount

                # 로또 기금에 세금 금액 추가
                lotto_path = os.path.join(FOLDER, "lotto.json")
                if not os.path.exists(lotto_path):
                    # 로또 파일이 없으면 기본값을 설정하여 생성
                    lotto_data = {"cash": 0, "stocks": {}}
                else:
                    try:
                        with open(lotto_path, "r", encoding="utf-8") as f:
                            lotto_data = json.load(f)
                    except json.JSONDecodeError:
                        # JSON 오류가 발생하면 기본값으로 초기화
                        lotto_data = {"cash": 0, "stocks": {}}

                lotto_data["cash"] += tax_amount  # 세금 금액을 로또 기금에 추가

                # 로또 파일에 업데이트된 데이터 저장
                with open(lotto_path, "w", encoding="utf-8") as f:
                    json.dump(lotto_data, f, indent=4, ensure_ascii=False)

                # 계좌 정보 업데이트: 차감된 현금과 주식 정보 저장
                with open(account_path, "w", encoding="utf-8") as f:
                    json.dump(account_data, f, ensure_ascii=False, indent=4)

        if message.content.startswith("$tax check"):
            account_path = os.path.join(FOLDER, "account.json")
            tax_path = os.path.join(FOLDER, "tax.json")
            lotto_path = os.path.join(FOLDER, "lotto.json")

            with open(account_path, "r+", encoding="utf-8") as f:
                account_data = json.load(f)

            with open(tax_path, "r+", encoding="utf-8") as f:
                tax_data = json.load(f)

            with open(lotto_path, "r+", encoding="utf-8") as f:
                lotto_data = json.load(f)

            penalized_users = []
            for user_id, account in account_data.items():
                if user_id not in tax_data and account["cash"] >= 100000:
                    penalty_cash = int(account["cash"] * 탈세벌금)
                    penalty_stocks = {stock: int(amount * 주식탈세벌금) for stock, amount in account["stocks"].items()}

                    account["cash"] -= penalty_cash
                    for stock, amount in penalty_stocks.items():
                        account["stocks"][stock] -= amount
                        lotto_data["stocks"][stock] = lotto_data["stocks"].get(stock, 0) + amount

                    lotto_data["cash"] += penalty_cash
                    penalized_users.append(user_id)

            with open(account_path, "w", encoding="utf-8") as f:
                json.dump(account_data, f, indent=4, ensure_ascii=False)

            with open(lotto_path, "w", encoding="utf-8") as f:
                json.dump(lotto_data, f, indent=4, ensure_ascii=False)

            tax_data.clear()
            with open(tax_path, "w", encoding="utf-8") as f:
                json.dump(tax_data, f, indent=4, ensure_ascii=False)

            if penalized_users:
                await message.channel.send(f"세금을 내지 않은 유저에게 페널티를 적용했습니다: {', '.join(penalized_users)}")
            else:
                await message.channel.send("모든 유저가 세금을 납부했습니다.")

        if message.content.startswith("$lotto start"):
            lotto_player_path = os.path.join(FOLDER, "lotto_player.json")
            lotto_path = os.path.join(FOLDER, "lotto.json")
            account_path = os.path.join(FOLDER, "account.json")

            # lotto_player.json 파일 확인 (로또 참가자 목록)
            if os.path.exists(lotto_player_path):
                with open(lotto_player_path, 'r', encoding="utf-8") as f:
                    lotto_player_data = json.load(f)
            else:
                lotto_player_data = []

            if not lotto_player_data:
                await message.channel.send("로또에 참여한 유저가 없습니다.")
                return

            # lotto.json에서 기금 정보 확인
            if os.path.exists(lotto_path):
                with open(lotto_path, 'r', encoding="utf-8") as f:
                    lotto_data = json.load(f)
            else:
                await message.channel.send("로또 기금 정보가 없습니다.")
                return

            lotto_cash = lotto_data.get("cash", 0)
            lotto_stocks = lotto_data.get("stocks", {})

            if lotto_cash == 0 and not lotto_stocks:
                await message.channel.send("로또 기금이 비어있습니다.")
                return

            # 랜덤으로 유저 선정
            import random
            winner_id = random.choice(lotto_player_data)

            # 선정된 유저의 계좌 정보 확인
            with open(account_path, 'r', encoding="utf-8") as f:
                account_data = json.load(f)

            if winner_id not in account_data:
                await message.channel.send(f"{winner_id}님의 계좌가 없습니다.")
                return

            # 현금 지급
            winner_account = account_data[winner_id]
            winner_cash = winner_account["cash"]
            winner_stocks = winner_account["stocks"]

            # 랜덤으로 현금 지급
            if lotto_cash > 0:
                winner_cash += lotto_cash
                lotto_cash = 0  # 기금에서 현금이 전부 지급됨

            # 랜덤으로 주식 지급
            if lotto_stocks:
                stock_to_give = random.choice(list(lotto_stocks.keys()))
                stock_amount = lotto_stocks[stock_to_give]
                winner_stocks[stock_to_give] = winner_stocks.get(stock_to_give, 0) + stock_amount
                lotto_stocks[stock_to_give] = 0  # 주식이 지급됨

            # 지급 후 계좌 정보 업데이트
            winner_account["cash"] = winner_cash
            winner_account["stocks"] = winner_stocks

            # 업데이트된 계좌 정보를 account.json에 저장
            with open(account_path, 'w', encoding="utf-8") as f:
                json.dump(account_data, f, ensure_ascii=False, indent=4)

            # 로또 기금 정보 업데이트
            with open(lotto_path, 'w', encoding="utf-8") as f:
                json.dump({"cash": lotto_cash, "stocks": lotto_stocks}, f, ensure_ascii=False, indent=4)

            # 로또 참여자 목록에서 당첨자 제외 (선택 사항)
            # lotto_player_data.remove(winner_id)
            # with open(lotto_player_path, 'w', encoding="utf-8") as f:
            #     json.dump(lotto_player_data, f, ensure_ascii=False, indent=4)

            await message.channel.send(f"축하합니다! {winner_id}님이 로또에 당첨되었습니다!")

        if message.content.startswith("!bet"):
            stock_random()
            int_changer()
            args = message.content.split()
            if len(args) != 2:
                await message.channel.send("올바른 형식: `!bet <금액>`")
                return

            try:
                bet_amount = int(args[1])
            except ValueError:
                await message.channel.send("금액은 숫자여야 합니다.")
                return

            # 파일 경로 및 변수 설정
            account_path = ACCOUNT_FILE
            gamble_config_path = os.path.join(FOLDER, "gamble_config.json")
            gamble_reward_path = os.path.join(FOLDER, "gamble_reward.json")
            lotto_path = os.path.join(FOLDER, "lotto.json")

            # account.json 처리
            if not os.path.exists(account_path):
                with open(account_path, "w", encoding="utf-8") as f:
                    json.dump(FILES["account.json"], f, indent=4, ensure_ascii=False)

            with open(account_path, "r", encoding="utf-8") as f:
                try:
                    account_data = json.load(f)
                except json.JSONDecodeError:
                    account_data = {}

            user_id = str(message.author.id)
            if user_id not in account_data:
                await message.channel.send("계좌를 먼저 개설해주세요.")
                return

            if account_data[user_id]["cash"] < bet_amount:
                await message.channel.send("보유 현금이 부족합니다.")
                return

            account_data[user_id]["cash"] -= bet_amount

            # gamble_config.json 처리
            if not os.path.exists(gamble_config_path):
                with open(gamble_config_path, "w", encoding="utf-8") as f:
                    json.dump(FILES["gamble_config.json"], f, indent=4, ensure_ascii=False)

            with open(gamble_config_path, "r", encoding="utf-8") as f:
                try:
                    gamble_config = json.load(f)
                except json.JSONDecodeError:
                    gamble_config = FILES["gamble_config.json"]

            probability = gamble_config.get("probability", 50)

            # gamble_reward.json 처리
            if not os.path.exists(gamble_reward_path):
                with open(gamble_reward_path, "w", encoding="utf-8") as f:
                    json.dump(FILES["gamble_reward.json"], f, indent=4, ensure_ascii=False)

            with open(gamble_reward_path, "r", encoding="utf-8") as f:
                try:
                    reward_config = json.load(f)
                except json.JSONDecodeError:
                    reward_config = FILES["gamble_reward.json"]

            multiplier = reward_config.get("multiplier", 2)

            # lotto.json 처리
            if not os.path.exists(lotto_path):
                with open(lotto_path, "w", encoding="utf-8") as f:
                    json.dump(FILES["lotto.json"], f, indent=4, ensure_ascii=False)

            with open(lotto_path, "r", encoding="utf-8") as f:
                try:
                    lotto_data = json.load(f)
                except json.JSONDecodeError:
                    lotto_data = FILES["lotto.json"]

            # 성공 여부 판단
            import random
            success = random.randint(1, 100) <= probability

            if success:
                winnings = bet_amount * multiplier
                account_data[user_id]["cash"] += winnings
                result = f"성공! {winnings}원을 획득했습니다."
            else:
                lotto_data["cash"] += bet_amount
                result = "실패했습니다. 금액이 로또 기금으로 전환되었습니다."

            # 결과 저장
            with open(account_path, "w", encoding="utf-8") as f:
                json.dump(account_data, f, indent=4, ensure_ascii=False)

            with open(lotto_path, "w", encoding="utf-8") as f:
                json.dump(lotto_data, f, indent=4, ensure_ascii=False)

            await message.channel.send(result)

            user_id = str(message.author.id)  # 유저 ID 가져오기

            # tax_person.json 파일 확인
            if os.path.exists(TAX_PERSON_FILE):
                with open(TAX_PERSON_FILE, 'r', encoding="utf-8") as f:
                    tax_person_data = json.load(f)
            else:
                tax_person_data = {}

            import datetime
            today_date = datetime.datetime.now().strftime("%Y-%m-%d")  # 오늘 날짜

            # 납세 처리: 현금과 주식 확인 및 납세 진행
            account_path = os.path.join(FOLDER, "account.json")
            with open(account_path, "r", encoding="utf-8") as f:
                account_data = json.load(f)

            if user_id not in account_data:
                await message.channel.send("계좌가 존재하지 않습니다. 계좌를 개설해주세요.")
            else:
                user_account = account_data[user_id]
                cash_balance = user_account["cash"]

                tax_amount = cash_balance * 도박세금  # 소득세 10% 세금

                # 현금 차감
                user_account["cash"] -= tax_amount

                # 로또 기금에 세금 금액 추가
                lotto_path = os.path.join(FOLDER, "lotto.json")
                if not os.path.exists(lotto_path):
                    # 로또 파일이 없으면 기본값을 설정하여 생성
                    lotto_data = {"cash": 0, "stocks": {}}
                else:
                    try:
                        with open(lotto_path, "r", encoding="utf-8") as f:
                            lotto_data = json.load(f)
                    except json.JSONDecodeError:
                        # JSON 오류가 발생하면 기본값으로 초기화
                        lotto_data = {"cash": 0, "stocks": {}}

                lotto_data["cash"] += tax_amount  # 세금 금액을 로또 기금에 추가

                # 로또 파일에 업데이트된 데이터 저장
                with open(lotto_path, "w", encoding="utf-8") as f:
                    json.dump(lotto_data, f, indent=4, ensure_ascii=False)

                # 계좌 정보 업데이트: 차감된 현금과 주식 정보 저장
                with open(account_path, "w", encoding="utf-8") as f:
                    json.dump(account_data, f, ensure_ascii=False, indent=4)

        # !매수 명령어 처리
        elif message.content.startswith("!매수"):
            int_changer()
            args = message.content.split()[1:]  # 명령어 인자 분리
            user_id = str(message.author.id)  # 유저 ID 가져오기

            # 계좌 정보 불러오기
            with open(ACCOUNT_FILE, 'r') as f:
                account_data = json.load(f)

            # 주식 정보 불러오기
            with open(STOCK_FILE, 'r') as f:
                stock_data = json.load(f)

            # 유저가 계좌를 가지고 있는지 확인
            if user_id not in account_data:
                await message.channel.send("먼저 계좌를 개설하세요!")
                return

            # 필요한 인자 받기 (거래소, 주식 코드, 수량)
            if len(args) != 3:
                await message.channel.send("사용법: !매수 <거래소> <주식코드> <수량>")
                return

            exchange = args[0]  # 거래소
            stock_code = args[1]  # 주식 코드
            quantity = int(args[2])  # 수량을 정수로

            # 주식이 존재하는지 확인
            if stock_code not in stock_data:
                await message.channel.send(f"주식 {stock_code}는(은) {exchange}에 존재하지 않습니다.")
                return

            stock_price = stock_data[stock_code]['price']  # 주식 가격 가져오기
            total_cost = stock_price * quantity  # 총 비용 계산

            # 유저 계좌에서 현금 부족 여부 확인
            if account_data[user_id]["cash"] < total_cost:
                await message.channel.send("현금이 부족합니다.")
                return

            # 주식 매수 가능, 계좌 업데이트
            account_data[user_id]["cash"] -= total_cost  # 현금 차감
            if stock_code not in account_data[user_id]["stocks"]:
                account_data[user_id]["stocks"][stock_code] = 0
            account_data[user_id]["stocks"][stock_code] += quantity  # 주식 보유량 업데이트

            # 업데이트된 계좌 정보 저장
            with open(ACCOUNT_FILE, 'w') as f:
                json.dump(account_data, f, indent=4)

            user_id = str(message.author.id)  # 유저 ID 가져오기

            # tax_person.json 파일 확인
            if os.path.exists(TAX_PERSON_FILE):
                with open(TAX_PERSON_FILE, 'r', encoding="utf-8") as f:
                    tax_person_data = json.load(f)
            else:
                tax_person_data = {}

            import datetime
            today_date = datetime.datetime.now().strftime("%Y-%m-%d")  # 오늘 날짜

            # 납세 처리: 현금과 주식 확인 및 납세 진행
            account_path = os.path.join(FOLDER, "account.json")
            with open(account_path, "r", encoding="utf-8") as f:
                account_data = json.load(f)

            if user_id not in account_data:
                await message.channel.send("계좌가 존재하지 않습니다. 계좌를 개설해주세요.")
            else:
                user_account = account_data[user_id]
                cash_balance = user_account["cash"]

                tax_amount = cash_balance * 매수세금  # 소득세 10% 세금

                # 현금 차감
                user_account["cash"] -= tax_amount

                # 로또 기금에 세금 금액 추가
                lotto_path = os.path.join(FOLDER, "lotto.json")
                if not os.path.exists(lotto_path):
                    # 로또 파일이 없으면 기본값을 설정하여 생성
                    lotto_data = {"cash": 0, "stocks": {}}
                else:
                    try:
                        with open(lotto_path, "r", encoding="utf-8") as f:
                            lotto_data = json.load(f)
                    except json.JSONDecodeError:
                        # JSON 오류가 발생하면 기본값으로 초기화
                        lotto_data = {"cash": 0, "stocks": {}}

                lotto_data["cash"] += tax_amount  # 세금 금액을 로또 기금에 추가

                # 로또 파일에 업데이트된 데이터 저장
                with open(lotto_path, "w", encoding="utf-8") as f:
                    json.dump(lotto_data, f, indent=4, ensure_ascii=False)

                # 계좌 정보 업데이트: 차감된 현금과 주식 정보 저장
                with open(account_path, "w", encoding="utf-8") as f:
                    json.dump(account_data, f, ensure_ascii=False, indent=4)

            await message.channel.send(f"{quantity}개의 {stock_code} 주식을 매수했습니다. 잔액: {account_data[user_id]['cash']} 원")
            stock_random()
            int_changer()

        # !매도 명령어 처리
        elif message.content.startswith("!매도"):
            int_changer()
            args = message.content.split()[1:]  # 명령어 인자 분리
            user_id = str(message.author.id)  # 유저 ID 가져오기

            # 계좌 정보 불러오기
            with open(ACCOUNT_FILE, 'r') as f:
                account_data = json.load(f)

            # 주식 정보 불러오기
            with open(STOCK_FILE, 'r') as f:
                stock_data = json.load(f)

            # 유저가 계좌를 가지고 있는지 확인
            if user_id not in account_data:
                await message.channel.send("먼저 계좌를 개설하세요!")
                return

            # 필요한 인자 받기 (거래소, 주식 코드, 수량)
            if len(args) != 3:
                await message.channel.send("사용법: !매도 <거래소> <주식코드> <수량>")
                return

            exchange = args[0]  # 거래소
            stock_code = args[1]  # 주식 코드
            quantity = int(args[2])  # 수량을 정수로

            # 유저가 보유한 주식 확인
            if stock_code not in account_data[user_id]["stocks"] or account_data[user_id]["stocks"][stock_code] < quantity:
                await message.channel.send(f"보유한 {stock_code} 주식이 부족합니다.")
                return

            stock_price = stock_data[stock_code]['price']  # 주식 가격 가져오기
            total_sale = stock_price * quantity  # 총 판매액 계산

            # 주식 매도 가능, 계좌 업데이트
            account_data[user_id]["cash"] += total_sale  # 현금 증가
            account_data[user_id]["stocks"][stock_code] -= quantity  # 주식 보유량 감소

            # 주식 보유량이 0이면 해당 주식을 딕셔너리에서 삭제
            if account_data[user_id]["stocks"][stock_code] == 0:
                del account_data[user_id]["stocks"][stock_code]

            # 업데이트된 계좌 정보 저장
            with open(ACCOUNT_FILE, 'w') as f:
                json.dump(account_data, f, indent=4)

            user_id = str(message.author.id)  # 유저 ID 가져오기

            # tax_person.json 파일 확인
            if os.path.exists(TAX_PERSON_FILE):
                with open(TAX_PERSON_FILE, 'r', encoding="utf-8") as f:
                    tax_person_data = json.load(f)
            else:
                tax_person_data = {}

            import datetime
            today_date = datetime.datetime.now().strftime("%Y-%m-%d")  # 오늘 날짜

            # 납세 처리: 현금과 주식 확인 및 납세 진행
            account_path = os.path.join(FOLDER, "account.json")
            with open(account_path, "r", encoding="utf-8") as f:
                account_data = json.load(f)

            if user_id not in account_data:
                await message.channel.send("계좌가 존재하지 않습니다. 계좌를 개설해주세요.")
            else:
                user_account = account_data[user_id]
                cash_balance = user_account["cash"]

                tax_amount = cash_balance * 매도세금 # 소득세 10% 세금

                # 현금 차감
                user_account["cash"] -= tax_amount

                # 로또 기금에 세금 금액 추가
                lotto_path = os.path.join(FOLDER, "lotto.json")
                if not os.path.exists(lotto_path):
                    # 로또 파일이 없으면 기본값을 설정하여 생성
                    lotto_data = {"cash": 0, "stocks": {}}
                else:
                    try:
                        with open(lotto_path, "r", encoding="utf-8") as f:
                            lotto_data = json.load(f)
                    except json.JSONDecodeError:
                        # JSON 오류가 발생하면 기본값으로 초기화
                        lotto_data = {"cash": 0, "stocks": {}}

                lotto_data["cash"] += tax_amount  # 세금 금액을 로또 기금에 추가

                # 로또 파일에 업데이트된 데이터 저장
                with open(lotto_path, "w", encoding="utf-8") as f:
                    json.dump(lotto_data, f, indent=4, ensure_ascii=False)

                # 계좌 정보 업데이트: 차감된 현금과 주식 정보 저장
                with open(account_path, "w", encoding="utf-8") as f:
                    json.dump(account_data, f, ensure_ascii=False, indent=4)

            await message.channel.send(f"{quantity}개의 {stock_code} 주식을 매도했습니다. 잔액: {account_data[user_id]['cash']} 원")
            stock_random()
            int_changer()

        if message.content.startswith("!주식기록"):
            stock_random()
            int_changer()
            history_path = os.path.join(FOLDER, "history.json")
            args = message.content.split()

            if len(args) != 3:
                await message.channel.send("올바른 형식: `!주식기록 <거래소> <주식코드>`")
                return

            exchange = args[1]
            stock_code = args[2]

            try:
                # history.json 읽기
                if not os.path.exists(history_path):
                    await message.channel.send("기록이 없습니다. `history.json` 파일이 존재하지 않습니다.")
                    return

                with open(history_path, "r", encoding="utf-8") as f:
                    history_data = json.load(f)

                # 조건에 맞는 기록 필터링
                filtered_records = [
                    record for record in history_data
                    if record.get("exchange") == exchange and record.get("name") == stock_code
                ]

                if not filtered_records:
                    await message.channel.send(f"{exchange} 거래소에서 코드 {stock_code}에 대한 기록이 없습니다.")
                    return

                # 결과 메시지 생성
                response = f"**{exchange} 거래소 - 주식 코드 {stock_code} 기록**\n"
                for record in filtered_records:
                    response += f"- 시간: {record['time']}, 주식명: {record['name']}, 가격: {record['price']}원\n"

                await message.channel.send(response)

            except Exception as e:
                await message.channel.send(f"주식 기록 조회 중 오류가 발생했습니다: {e}")

        if message.content.startswith("!주식정보"):
            stock_random()
            int_changer()
            args = message.content.split()
            if len(args) != 3:
                await message.channel.send("올바른 형식: `!주식정보 <거래소> <주식코드>`")
                return

            stock_code = args[2]
            stock_path = os.path.join(FOLDER, "stock.json")

            with open(stock_path, "r", encoding="utf-8") as f:
                stock_data = json.load(f)

            if stock_code not in stock_data:
                await message.channel.send("해당 주식이 존재하지 않습니다.")
                return

            stock_info = stock_data[stock_code]
            embed = discord.Embed(title=f"📄 주식 정보: {stock_info['name']} ({stock_code})", color=0x0000FF)
            embed.add_field(name="거래소", value=stock_info["exchange"], inline=False)
            embed.add_field(name="가격", value=f"{stock_info['price']}원", inline=False)
            embed.add_field(name="발행 주식 수", value=f"{stock_info['total_shares']}주", inline=False)
            embed.add_field(name="거래 가능 주식 수", value=f"{stock_info['tradable_shares']}주", inline=False)

            await message.channel.send(embed=embed)

        if message.content.startswith("!주식기록"):
            stock_random()
            int_changer()
            args = message.content.split()
            if len(args) != 3:
                await message.channel.send("올바른 형식: `!주식기록 <거래소> <주식코드>`")
                return

            exchange, stock_code = args[1], args[2]
            history_path = os.path.join(FOLDER, "history.json")
            stock_path = os.path.join(FOLDER, "stock.json")

            # 주식 존재 여부 확인
            with open(stock_path, "r", encoding="utf-8") as f:
                stock_data = json.load(f)

            if stock_code not in stock_data or stock_data[stock_code]["exchange"] != exchange:
                await message.channel.send("해당 주식이 존재하지 않습니다.")
                return

            # 변동 기록 조회
            try:
                with open(history_path, "r", encoding="utf-8") as f:
                    history_data = json.load(f)
            except FileNotFoundError:
                await message.channel.send("변동 기록이 없습니다.")
                return

            stock_history = [record for record in history_data if record["stock_code"] == stock_code and record["exchange"] == exchange]

            if not stock_history:
                await message.channel.send("해당 주식의 변동 기록이 없습니다.")
                return

            # 임베드 메시지로 출력
            embed = discord.Embed(
                title=f"📊 {stock_data[stock_code]['name']} ({stock_code}) 변동 기록",
                description=f"거래소: {exchange}",
                color=discord.Color.blue()
            )

            for record in stock_history[-10:]:  # 최근 10개의 기록만 표시
                timestamp = record["timestamp"]
                price_change = record["price_change"]
                embed.add_field(
                    name=timestamp,
                    value=f"변동된 가격: {price_change}원",
                    inline=False
                )

            await message.channel.send(embed=embed)

        if message.content == "$stock random":
            import random
            from datetime import datetime

            stock_path = os.path.join(FOLDER, "stock.json")
            history_path = os.path.join(FOLDER, "history.json")

            try:
                # stock.json 읽기
                with open(stock_path, "r", encoding="utf-8") as f:
                    stock_data = json.load(f)

                if not stock_data:
                    await message.channel.send("등록된 주식이 없습니다.")
                    return

                # history.json 읽기 (없으면 초기화)
                if not os.path.exists(history_path):
                    with open(history_path, "w", encoding="utf-8") as f:
                        json.dump([], f, indent=4, ensure_ascii=False)

                with open(history_path, "r", encoding="utf-8") as f:
                    history_data = json.load(f)

                # 모든 주식의 가격 랜덤 변경
                for stock_key, stock_info in stock_data.items():
                    # 기존 가격 가져오기
                    current_price = stock_info.get("price", 100)

                    # 상승/하락 비율 설정 (상승 확률 60%, 하락 확률 50%)
                    if random.random() < 0.6:  # 60% 확률로 상승
                        random_factor = random.uniform(1.01, 1.2)  # +1% ~ +20%
                    else:  # 40% 확률로 하락
                        random_factor = random.uniform(0.9, 0.99)  # -1% ~ -10%

                    new_price = max(10000, int(current_price * random_factor))  # 가격은 최소 1원 이상

                    # 주식 정보 업데이트
                    stock_info["price"] = new_price

                    # history.json에 변경 기록 추가
                    history_entry = {
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "exchange": stock_info.get("exchange", "Unknown"),  # 거래소 정보
                        "code": stock_info.get("code", "Unknown"),  # 주식 코드
                        "name": stock_key,  # 주식명 (키 값)
                        "price": new_price  # 한 주당 주가
                    }
                    history_data.append(history_entry)

                # stock.json 업데이트
                with open(stock_path, "w", encoding="utf-8") as f:
                    json.dump(stock_data, f, indent=4, ensure_ascii=False)

                # history.json 업데이트
                with open(history_path, "w", encoding="utf-8") as f:
                    json.dump(history_data, f, indent=4, ensure_ascii=False)

                await message.channel.send("모든 주식의 가격이 랜덤하게 변경되고, 변경 이력이 저장되었습니다!")

            except Exception as e:
                await message.channel.send(f"주식 가격 변경 중 오류가 발생했습니다: {e}")

        if message.content == "$reset_daily_rewards":
            # daily_reward.json 파일 경로
            daily_reward_path = os.path.join(FOLDER, "daily_reward.json")

            # daily_reward.json 파일 초기화
            try:
                with open(daily_reward_path, "w", encoding="utf-8") as f:
                    json.dump([], f, ensure_ascii=False, indent=4)
                await message.channel.send("Daily reward 기록이 초기화되었습니다!")
            except Exception as e:
                await message.channel.send(f"초기화에 실패했습니다: {e}")

        if message.content == "$reset_tax_person":
            # tax_person.json 파일 경로
            tax_person_path = os.path.join(FOLDER, "tax_person.json")

            # tax_person.json 파일 초기화
            try:
                with open(tax_person_path, "w", encoding="utf-8") as f:
                    json.dump([], f, ensure_ascii=False, indent=4)
                await message.channel.send("tax person 기록이 초기화되었습니다!")
            except Exception as e:
                await message.channel.send(f"초기화에 실패했습니다: {e}")

        if message.content == "$reset_lotto_player":
            # lotto_player.json 파일 경로
            lotto_player_path = os.path.join(FOLDER, "lotto_player.json")

            # lotto_player.json 파일 초기화
            try:
                with open(lotto_player_path, "w", encoding="utf-8") as f:
                    json.dump([], f, ensure_ascii=False, indent=4)
                await message.channel.send("lotto player 기록이 초기화되었습니다!")
            except Exception as e:
                await message.channel.send(f"초기화에 실패했습니다: {e}")

        if message.content == "$reset_history":
            # history.json 파일 경로
            history_path = os.path.join(FOLDER, "history.json")

            # history.json 파일 초기화
            try:
                with open(history_path, "w", encoding="utf-8") as f:
                    json.dump([], f, ensure_ascii=False, indent=4)
                await message.channel.send("주식기록이 초기화되었습니다!")
            except Exception as e:
                await message.channel.send(f"초기화에 실패했습니다: {e}")

        if message.content.startswith("$stock publish"):
            args = message.content.split()
            if len(args) != 8:
                await message.channel.send("올바른 형식: `$stock publish <주식명> <거래소> <카테고리> <주당 가격> <발행 주식 수> <거래 가능한 비율>`")
                return

            stock_name = args[2]
            exchange = args[3]
            category = args[4]
            price = int(args[5])
            total_shares = int(args[6])
            tradable_ratio = float(args[7])

            stock_path = os.path.join(FOLDER, "stock.json")

            with open(stock_path, "r", encoding="utf-8") as f:
                stock_data = json.load(f)

            new_stock_code = f"{len(stock_data):06d}"

            stock_data[new_stock_code] = {
                "name": stock_name,
                "exchange": exchange,
                "category": category,
                "price": price,
                "total_shares": total_shares,
                "tradable_shares": total_shares * (tradable_ratio/100)
            }

            with open(stock_path, "w", encoding="utf-8") as f:
                json.dump(stock_data, f, ensure_ascii=False, indent=4)

            await message.channel.send(f"주식 {stock_name} ({new_stock_code}) 가 발행되었습니다!")

        if message.content.startswith("$stock delist"):
            args = message.content.split()
            if len(args) != 4:
                await message.channel.send("올바른 형식: `$stock delist <거래소> <주식코드>`")
                return

            exchange = args[2]
            stock_code = args[3]

            stock_path = os.path.join(FOLDER, "stock.json")
            account_path = os.path.join(FOLDER, "account.json")

            with open(stock_path, "r", encoding="utf-8") as f:
                stock_data = json.load(f)

            if stock_code not in stock_data or stock_data[stock_code]["exchange"] != exchange:
                await message.channel.send("해당 주식이 존재하지 않거나 거래소가 맞지 않습니다.")
                return

            del stock_data[stock_code]

            with open(stock_path, "w", encoding="utf-8") as f:
                json.dump(stock_data, f, ensure_ascii=False, indent=4)

            with open(account_path, "r", encoding="utf-8") as f:
                account_data = json.load(f)

            for user_id, account in account_data.items():
                if stock_code in account['stocks']:
                    del account['stocks'][stock_code]

            with open(account_path, "w", encoding="utf-8") as f:
                json.dump(account_data, f, ensure_ascii=False, indent=4)

            await message.channel.send(f"{stock_code} 주식이 상장 폐지되었습니다.")

        if message.content.startswith("$stock plus"):
            args = message.content.split()
            if len(args) != 5:
                await message.channel.send("올바른 형식: `$stock plus <거래소> <주식코드> <가격 증가액>`")
                return

            exchange = args[2]
            stock_code = args[3]
            price_increase = int(args[4])

            stock_path = os.path.join(FOLDER, "stock.json")

            with open(stock_path, "r", encoding="utf-8") as f:
                stock_data = json.load(f)

            if stock_code not in stock_data or stock_data[stock_code]["exchange"] != exchange:
                await message.channel.send("해당 주식이 존재하지 않습니다.")
                return

            stock_data[stock_code]["price"] += price_increase

            with open(stock_path, "w", encoding="utf-8") as f:
                json.dump(stock_data, f, ensure_ascii=False, indent=4)

            await message.channel.send(f"{stock_code}의 주식 가격이 {price_increase}만큼 증가했습니다.")

        if message.content.startswith("$stock minus"):
            args = message.content.split()
            if len(args) != 5:
                await message.channel.send("올바른 형식: `$stock minus <거래소> <주식코드> <가격 감소액>`")
                return

            exchange = args[2]
            stock_code = args[3]
            price_decrease = int(args[4])

            stock_path = os.path.join(FOLDER, "stock.json")

            with open(stock_path, "r", encoding="utf-8") as f:
                stock_data = json.load(f)

            if stock_code not in stock_data or stock_data[stock_code]["exchange"] != exchange:
                await message.channel.send("해당 주식이 존재하지 않습니다.")
                return

            stock_data[stock_code]["price"] -= price_decrease

            with open(stock_path, "w", encoding="utf-8") as f:
                json.dump(stock_data, f, ensure_ascii=False, indent=4)

            await message.channel.send(f"{stock_code}의 주식 가격이 {price_decrease}만큼 감소했습니다.")

        if message.content.startswith("$stock set"):
            args = message.content.split()
            if len(args) != 5:
                await message.channel.send("올바른 형식: `$stock set <거래소> <주식코드> <새로운 가격>`")
                return

            exchange = args[2]
            stock_code = args[3]
            new_price = int(args[4])

            stock_path = os.path.join(FOLDER, "stock.json")

            with open(stock_path, "r", encoding="utf-8") as f:
                stock_data = json.load(f)

            if stock_code not in stock_data or stock_data[stock_code]["exchange"] != exchange:
                await message.channel.send("해당 주식이 존재하지 않습니다.")
                return

            stock_data[stock_code]["price"] = new_price

            with open(stock_path, "w", encoding="utf-8") as f:
                json.dump(stock_data, f, ensure_ascii=False, indent=4)

            await message.channel.send(f"{stock_code}의 주식 가격이 {new_price}로 설정되었습니다.")

        if message.content.startswith("$stock split"):
            args = message.content.split()
            if len(args) != 5:
                await message.channel.send("올바른 형식: `$stock split <거래소> <주식코드> <분할 비율>`")
                return

            exchange = args[2]
            stock_code = args[3]
            split_ratio = int(args[4])

            stock_path = os.path.join(FOLDER, "stock.json")

            with open(stock_path, "r", encoding="utf-8") as f:
                stock_data = json.load(f)

            if stock_code not in stock_data or stock_data[stock_code]["exchange"] != exchange:
                await message.channel.send("해당 주식이 존재하지 않습니다.")
                return

            stock_data[stock_code]["total_shares"] *= split_ratio
            stock_data[stock_code]["tradable_shares"] *= split_ratio

            with open(stock_path, "w", encoding="utf-8") as f:
                json.dump(stock_data, f, ensure_ascii=False, indent=4)

            await message.channel.send(f"{stock_code}의 주식이 액면분할되었습니다.")

        if message.content.startswith("$stock merge"):
            args = message.content.split()
            if len(args) != 5:
                await message.channel.send("올바른 형식: `$stock merge <거래소> <주식코드> <병합 비율>`")
                return

            exchange = args[2]
            stock_code = args[3]
            merge_ratio = int(args[4])

            stock_path = os.path.join(FOLDER, "stock.json")

            with open(stock_path, "r", encoding="utf-8") as f:
                stock_data = json.load(f)

            if stock_code not in stock_data or stock_data[stock_code]["exchange"] != exchange:
                await message.channel.send("해당 주식이 존재하지 않습니다.")
                return

            stock_data[stock_code]["total_shares"] //= merge_ratio

        # !이체 명령어 처리
        if message.content.startswith("!이체"):
            int_changer()
            args = message.content.split()[1:]  # 명령어 인자 분리
            user_id = str(message.author.id)  # 유저 ID 가져오기

            # 계좌 정보 불러오기
            with open(ACCOUNT_FILE, 'r') as f:
                account_data = json.load(f)

            # 필요한 인자 받기 (목표 유저와 금액)
            if len(args) != 2:
                await message.channel.send("사용법: !이체 <유저멘션> <금액>")
                return

            target_user = args[0]  # 타겟 유저
            transfer_amount = int(args[1])  # 이체할 금액

            # 유저가 계좌를 가지고 있는지 확인
            if user_id not in account_data:
                await message.channel.send("먼저 계좌를 개설하세요!")
                return

            # 이체할 금액이 유저의 현금보다 많은지 확인
            if account_data[user_id]["cash"] < transfer_amount:
                await message.channel.send("현금이 부족합니다.")
                return

            # 타겟 유저가 계좌를 가지고 있는지 확인
            if target_user not in account_data:
                await message.channel.send(f"{target_user} 님은 계좌가 없습니다.")
                return

            # 이체 진행
            account_data[user_id]["cash"] -= transfer_amount  # 보내는 사람 차감
            account_data[target_user]["cash"] += transfer_amount  # 받는 사람 추가

            # 계좌 업데이트
            with open(ACCOUNT_FILE, 'w') as f:
                json.dump(account_data, f, indent=4)

            await message.channel.send(f"{transfer_amount}원이 {target_user}님에게 이체되었습니다.")

        if message.content.startswith("$account"):
            args = message.content.split()

            if len(args) != 4:
                await message.channel.send("사용법: $account <add/del/set> <유저id> <금액>")
                return

            action = args[1]
            user_id = args[2]
            amount = int(args[3])

            # 계좌 파일 로딩
            account_path = os.path.join(FOLDER, "account.json")
            with open(account_path, "r", encoding="utf-8") as f:
                account_data = json.load(f)

            if action == "add":
                if user_id not in account_data:
                    await message.channel.send("해당 유저는 계좌가 없습니다.")
                    return
                account_data[user_id]["cash"] += amount
                await message.channel.send(f"{user_id} 계좌에 {amount}원이 추가되었습니다.")

            elif action == "del":
                if user_id not in account_data:
                    await message.channel.send("해당 유저는 계좌가 없습니다.")
                    return
                account_data[user_id]["cash"] -= amount
                await message.channel.send(f"{user_id} 계좌에서 {amount}원이 차감되었습니다.")

            elif action == "set":
                if user_id not in account_data:
                    await message.channel.send("해당 유저는 계좌가 없습니다.")
                    return
                account_data[user_id]["cash"] = amount
                await message.channel.send(f"{user_id} 계좌의 금액이 {amount}으로 설정되었습니다.")

            # 업데이트된 계좌 저장
            with open(account_path, "w", encoding="utf-8") as f:
                json.dump(account_data, f, ensure_ascii=False, indent=4)

        # !지갑 명령어 처리
        if message.content.startswith("!지갑"):
            stock_random()
            int_changer()
            user_id = str(message.author.id)

            # 계좌 정보 로딩
            account_path = os.path.join(FOLDER, "account.json")
            with open(account_path, "r", encoding="utf-8") as f:
                account_data = json.load(f)

            if user_id not in account_data:
                await message.channel.send("계좌가 존재하지 않습니다. 계좌를 개설해주세요.")
                return

            # 유저 계좌 정보
            user_account = account_data[user_id]
            cash = user_account["cash"]
            stocks = user_account["stocks"]

            # 주식 정보 출력 및 자산 계산
            stock_message = ""
            total_stock_value = 0  # 주식 총 가치를 계산할 변수
            with open(STOCK_FILE, "r", encoding="utf-8") as f:
                stock_data = json.load(f)

            for stock_key, quantity in stocks.items():
                stock_info = stock_data.get(stock_key)
                if stock_info:
                    exchange = stock_info.get("exchange")
                    stock_name = stock_info.get("name", "알 수 없는 주식")
                    stock_price = stock_info.get("price", 0)  # 주식의 현재 가격을 가져옴
                    stock_value = stock_price * quantity  # 주식의 총 가치를 계산
                    total_stock_value += stock_value  # 총 자산에 더하기
                    stock_message += f"거래소: {exchange}, 이름: {stock_name}, 수량: {quantity}, 현재가: {stock_price}원, 자산 가치: {stock_value}원\n"
                else:
                    stock_message += f"거래소, 코드 정보 없음: {stock_key}, 수량: {quantity}\n"

            # 총 자산 계산 (현금 + 주식 자산)
            total_assets = cash + total_stock_value

            # 임베드로 계좌 정보 출력
            embed = discord.Embed(title=f"{message.author.name}님의 지갑", color=discord.Color.blue())
            embed.add_field(name="현금", value=f"{cash}원", inline=False)
            embed.add_field(name="보유 주식", value=stock_message if stock_message else "보유한 주식이 없습니다.", inline=False)
            embed.add_field(name="총 자산", value=f"{total_assets}원", inline=False)
            await message.channel.send(embed=embed)

        if message.content.startswith("$gamble"):
            args = message.content.split()

            if len(args) != 3:
                await message.channel.send("사용법: $gamble <probability/reward> <값>")
                return

            setting_type = args[1]
            value = float(args[2])

            gamble_config_path = os.path.join(FOLDER, "gamble_config.json")
            gamble_reward_path = os.path.join(FOLDER, "gamble_reward.json")

            if setting_type == "probability":
                # 도박 확률 설정
                with open(gamble_config_path, "r", encoding="utf-8") as f:
                    gamble_config = json.load(f)

                gamble_config["probability"] = value

                with open(gamble_config_path, "w", encoding="utf-8") as f:
                    json.dump(gamble_config, f, ensure_ascii=False, indent=4)

                await message.channel.send(f"도박의 성공 확률이 {value}%로 설정되었습니다.")

            elif setting_type == "reward":
                # 보상 배율 설정
                with open(gamble_reward_path, "r", encoding="utf-8") as f:
                    gamble_reward = json.load(f)

                gamble_reward["multiplier"] = value

                with open(gamble_reward_path, "w", encoding="utf-8") as f:
                    json.dump(gamble_reward, f, ensure_ascii=False, indent=4)

                await message.channel.send(f"도박의 보상 배율이 {value}로 설정되었습니다.")

        if message.content == "!로또체크":
            lotto_path = os.path.join(FOLDER, "lotto.json")
            stock_path = os.path.join(FOLDER, "stock.json")

            try:
                # lotto.json 파일 읽기
                with open(lotto_path, "r", encoding="utf-8") as f:
                    lotto_data = json.load(f)

                # 현금 추출
                total_value = lotto_data["cash"]

                # 주식 가격 계산
                with open(stock_path, "r", encoding="utf-8") as f:
                    stock_data = json.load(f)

                # stocks 필드가 딕셔너리이므로, 주식 코드와 수량을 확인하여 가치 계산
                for stock_code, stock_quantity in lotto_data["stocks"].items():
                    # 주식 코드로 stock.json에서 현재 주식 가격 조회
                    current_price = stock_data.get(stock_code, {}).get("price", 0)

                    # 주식의 총 가치를 계산하여 더함
                    total_value += current_price * stock_quantity

                # 결과 출력
                await message.channel.send(f"현재 로또 기금의 총 가치는 {total_value}원입니다.")

            except Exception as e:
                await message.channel.send(f"로또 기금 체크 중 오류가 발생했습니다: {e}")

        if message.content == "!주식목록":
            stock_random()
            int_changer()
            stock_path = os.path.join(FOLDER, "stock.json")

            try:
                # stock.json 파일 읽기
                with open(stock_path, "r", encoding="utf-8") as f:
                    stock_data = json.load(f)

                if not stock_data:
                    await message.channel.send("등록된 주식이 없습니다.")
                    return

                # 임베드 메시지 생성
                embed = discord.Embed(title="주식 목록", description="등록된 주식들의 정보를 아래에서 확인하세요.", color=discord.Color.blue())

                for stock_key, stock_info in stock_data.items():
                    stock_name = stock_info.get("name", "이름 없음")  # 주식명
                    stock_price = stock_info.get("price", 0)  # 주식 가격
                    stock_exchange = stock_info.get("exchange", "거래소 없음")  # 거래소

                    # 각 주식 정보를 임베드에 추가
                    embed.add_field(
                        name=f"{stock_name} ({stock_key})",
                        value=f"거래소: {stock_exchange}\n현재 가격: {stock_price}원",
                        inline=False
                    )

                await message.channel.send(embed=embed)

            except Exception as e:
                await message.channel.send(f"주식 목록 조회 중 오류가 발생했습니다: {e}")

        if message.content == "!랭킹":
            stock_random()
            int_changer()
            import operator

            account_path = os.path.join(FOLDER, "account.json")
            stock_path = os.path.join(FOLDER, "stock.json")

            try:
                # account.json 읽기
                with open(account_path, "r", encoding="utf-8") as f:
                    account_data = json.load(f)

                # stock.json 읽기
                with open(stock_path, "r", encoding="utf-8") as f:
                    stock_data = json.load(f)

                # 유저별 총 자산 계산
                user_assets = {}
                for user_id, account_info in account_data.items():
                    # 현금 자산
                    total_assets = account_info.get("cash", 0)

                    # 주식 자산
                    stocks = account_info.get("stocks", {})
                    for stock_code, quantity in stocks.items():
                        stock_price = stock_data.get(stock_code, {}).get("price", 0)
                        total_assets += stock_price * quantity  # 주식 가격 * 보유 수량

                    # 총 자산 저장
                    user_assets[user_id] = total_assets

                # 총 자산 기준으로 정렬
                sorted_users = sorted(user_assets.items(), key=operator.itemgetter(1), reverse=True)

                # 순위 표시
                embed = discord.Embed(
                    title="🏆 총 자산 순위",
                    description="유저들의 총 자산 순위를 확인하세요!",
                    color=discord.Color.gold()
                )
                for rank, (user_id, assets) in enumerate(sorted_users, start=1):
                    user = await client.fetch_user(user_id)  # 유저 이름 가져오기
                    embed.add_field(name=f"{rank}위: {user.name}", value=f"총 자산: {assets:,.2f}원", inline=False)

                await message.channel.send(embed=embed)

            except Exception as e:
                await message.channel.send(f"랭킹 계산 중 오류가 발생했습니다: {e}")

        if message.content == "$cmd":
            stock_random()
            int_changer()
            embed = discord.Embed(title="사용 가능한 명령어 목록", color=0x3498db)

            # 명령어 설명 추가
            embed.add_field(name="$cmd", value="명령어와 설명을 볼 수 있습니다.", inline=False)
            embed.add_field(name="$nmd <갯수>", value="<갯수>만큼 메시지를 삭제할 수 있습니다.", inline=False)
            embed.add_field(name="!계좌개설", value="계좌를 생성하고 초기 자금을 설정합니다.", inline=False)
            embed.add_field(name="!이체 <플레이어id> <금액>", value="다른 플레이어에게 금액을 송금합니다.", inline=False)
            embed.add_field(name="!일급", value="하루에 한 번 50,000원을 지급받습니다.", inline=False)
            embed.add_field(name="!주식목록", value="현재 상장된 모든 주식의 정보를 확인합니다.", inline=False)
            embed.add_field(name="!매수 <주식명> <수량>", value="원하는 주식을 지정한 수량만큼 구매합니다.", inline=False)
            embed.add_field(name="!매도 <주식명> <수량>", value="보유 중인 주식을 지정한 수량만큼 판매합니다.", inline=False)
            embed.add_field(name="!주식정보 <주식명>", value="특정 주식의 정보를 확인합니다.", inline=False)
            embed.add_field(name="!지갑", value="현재 자신의 계좌 잔고를 확인합니다.", inline=False)
            embed.add_field(name="!주식기록 <주식명>", value="특정 주식의 가격 변동 기록을 확인합니다.", inline=False)
            embed.add_field(name="!bet <금액>", value="도박을 할 수 있습니다. 금액을 설정하고 도박에 참여하세요.", inline=False)
            embed.add_field(name="!운세", value="운세를 볼 수 있습니다.", inline=False)
            embed.add_field(name="!궁합 <유저1> <유저2>", value="궁합을 볼 수 있습니다. 유저 간의 궁합을 시험해보세요.", inline=False)
            embed.add_field(name="!로또참여", value="10만원을 내고 로또에 참가할 수 있습니다. 당신의 운을 시험해보세요.", inline=False)
            embed.add_field(name="!랭킹", value="총 자산의 순위을 볼 수 있습니다. 유저들의 자산을 확인해보세요.", inline=False)
            embed.add_field(name="!세율", value="세율을 볼 수 있습니다. 현행 세율을 확인해보세요.", inline=False)
            embed.add_field(name=f"!기부 <금액>", value="기부할 수 있습니다. 기부금은 교육, 의료, 식량, 의류, 주거, 봉사자나 재능기부자의 \n활동비나 실비 지원, 환경, 사회복지, 문화예술, 지방지역사회 활성화 등을 위해 사용됩니다.", inline=False)

            await message.channel.send(embed=embed)

        if message.content.startswith("!운세"):
            # 사용자가 랜덤으로 운세를 받음
            import random
            fortune = random.choice(fortunes)
            await message.channel.send(f"{message.author.mention}님의 운세: {fortune}")

        if message.content.startswith("!궁합"):
            # 두 명의 사용자 이름을 받음
            try:
                # 이름을 두 명으로 분리
                users = message.content.split()
                if len(users) != 3:
                    await message.channel.send("사용법: !궁합 @user1 @user2")
                    return

                user1 = users[1]
                user2 = users[2]

                # 궁합을 랜덤으로 선택
                import  random
                compatibility = random.choice(compatibilities)
                await message.channel.send(f"{user1}님과 {user2}님의 궁합: {compatibility}")

            except Exception as e:
                await message.channel.send(f"오류 발생: {e}")

        if message.content.startswith(''):
            time = message.created_at
            f = open('log.txt', 'a')
            f.write(f"{time} 에 {message.guild.name} 에서 {message.author.name} ( {message.author.nick} ) ( {message.author.mention} ) 가 {message.channel.mention} 에서 " + "'"+message.content+"'" + " 라고 말함. \n")
            f.close()

        if message.content.startswith('$nmd'):
            try:
                count = int(message.content.split()[1])
                deleted = await message.channel.purge(limit=count)
                await message.channel.send(f"{len(deleted)}개의 메시지가 삭제되었습니다.", delete_after=5)
            except (IndexError, ValueError):
                await message.channel.send("사용법: $nmd [숫자]", delete_after=5)
            except discord.Forbidden:
                await message.channel.send("메시지를 삭제할 권한이 없습니다.", delete_after=5)

        if message.attachments:
            for attachment in message.attachments:
                await save_image(attachment)

        if message.attachments:
            if not os.path.exists(folder):
                os.makedirs(folder)

            file_names = []
            for attachment in message.attachments:
                file_path = os.path.join(folder, attachment.filename)
                await attachment.save(file_path)
                file_names.append(attachment.filename)

    async def on_reaction_add(self, reaction, user):
        stock_random()
        if user.bot:
            return

        message_content = reaction.message.content
        reaction_emoji = reaction.emoji
        channel = reaction.message.channel
        message_time = reaction.message.created_at
        message_guild = reaction.message.guild

        now = datetime.now()
        time = f"{str(now.year)}년 {str(now.month)}월 {str(now.day)}일 {str(now.hour)}시 {str(now.minute)}분 {str(now.second)}초"

        f = open('log.txt', 'a')
        f.write(f"{time} 에 {user.name}이(가) {message_guild} 서버의 {message_time} 에 작성된 {channel} 에 있는 '{message_content}' 메시지에 {reaction_emoji} 이모지로 반응.\n")
        f.close()

    async def on_message_edit(self, before, after):
        stock_random()
        bc = before.content
        ac = after.content
        now = datetime.now()
        time = f"{str(now.year)}년 {str(now.month)}월 {str(now.day)}일 {str(now.hour)}시 {str(now.minute)}분 {str(now.second)}초"

        f = open('log.txt', 'a')
        f.write(f"{time} 에 {after.guild.name} 서버의 {after.channel} 에서 {after.author} 가 {before.author} 에 의해 {before.created_at} 에 작성된 ' {bc} ' 를 ' {ac} ' 로 수정 \n")
        f.close()

intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
client.run('MTMwNDgwNzE0MTYyMTYzMzAzNA.GdUT8R.8WbWmdYoOyQ_Zczcb1LtDHcrNG3nott8739kpQ')