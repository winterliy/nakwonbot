import json
import os
import time
# from discord.ext import commands
# from random import choice, randint
# import yt_dlp as youtube_dl
from datetime import datetime
from http import client
# import bs4
import discord
import sys
# from discord.sinks import WaveSink
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
# import aiohttp  # 비동기 요청 라이브러리
import signal
# import asyncio
# import wave

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

font_path = '/Users/sinjaehyeon/Library/Fonts/helvetica-light-587ebe5a59211.ttf'
font_name = fm.FontProperties(fname=font_path).get_name()

folder = 'file_log'
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
HISTORY_FILE = "economics/history.json"
USER_DATA_FILE = "user_data.json"
recording_files = "recording_files"
active_voice_clients = {}  # 서버별 활성화된 음성 클라이언트

try:
    with open(USER_DATA_FILE, "r") as file:
        user_data = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
    user_data = {}

# 종료 시 데이터 저장 핸들러
signal.signal(signal.SIGINT, lambda sig, frame: (json.dump(user_data, open(USER_DATA_FILE, "w"), indent=4), sys.exit(0)))


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
    "오늘은 사람들과의 "
    "관계에서 운이 따를 것입니다. 좋은 소식이 있을 거예요.",
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

earned_income_tax = 0.001
lottery_tax = 0.001
gambling_tax = 0.01
stock_purchase_tax = 0.001
stock_sales_tax = 0.001
transfer_tax = 0.01
basic_tax_rate = 0.003
tax_evasion_fine = 0.8
stock_tax_evasion_fine = 0.8
stock_floor_limit = 100
stock_increase_decrease_rate = 0.5
rich_tax_increase_rate = 0.5
standard_for_tax_increase_for_the_wealthy = 100000000000
reward = 150000

def price_fix(exchange, stock, price):
    price = int(price)

    stock_path = os.path.join(FOLDER, "stock.json")

    with open(stock_path, "r", encoding="utf-8") as stock_file:
        stock_data = json.load(stock_file)

    if stock not in stock_data or stock_data[stock]["exchange"] != exchange:
        print("해당 주식이 존재하지 않습니다.")
        return

    stock_data[stock]["price"] = price

    with open(stock_path, "w", encoding="utf-8") as stock_file:
        json.dump(stock_data, stock_file, ensure_ascii=False, indent=4)

    print(f"{stock}의 주식 가격이 {price}로 설정되었습니다.")

def stock_random():
    import random
    from datetime import datetime

    stock_path = os.path.join(FOLDER, "stock.json")
    history_path = os.path.join(FOLDER, "history.json")

    try:
        # stock.json 읽기
        with open(stock_path, "r", encoding="utf-8") as stock_file:
            stock_data = json.load(stock_file)

        if not stock_data:
            print("등록된 주식이 없습니다.")
            return

        # history.json 읽기 (없으면 초기화)
        if not os.path.exists(history_path):
            with open(history_path, "w", encoding="utf-8") as history_file:
                json.dump([], history_file, indent=4, ensure_ascii=False)

        with open(history_path, "r", encoding="utf-8") as history_file:
            history_data = json.load(history_file)

        # 모든 주식의 가격 랜덤 변경
        for stock_key, stock_info in stock_data.items():
            # 기존 가격 가져오기
            current_price = stock_info.get("price", 100)

            # 상승/하락 비율 설정 (상승 확률 60%, 하락 확률 50%)
            if random.random() < stock_increase_decrease_rate:  # 60% 확률로 상승
                random_factor = random.uniform(1.01, 1.2)  # +1% ~ +20%
            else:  # 40% 확률로 하락
                random_factor = random.uniform(0.9, 0.99)  # -1% ~ -10%

            new_price = max(stock_floor_limit, int(current_price * random_factor))  # 가격은 최소 1원 이상

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
        with open(stock_path, "w", encoding="utf-8") as stock_file:
            json.dump(stock_data, stock_file, indent=4, ensure_ascii=False)

        # history.json 업데이트
        with open(history_path, "w", encoding="utf-8") as history_file:
            json.dump(history_data, history_file, indent=4, ensure_ascii=False)

        print("모든 주식의 가격이 랜덤하게 변경되고, 변경 이력이 저장되었습니다!")

    except Exception as e:
        print(f"주식 가격 변경 중 오류가 발생했습니다: {e}")

def int_changer():
    try:
        # JSON 파일 읽기
        with open('economics/account.json', "r", encoding="utf-8") as account:
            account_data = json.load(account)

        # 데이터 변환
        for user_id, account_info in account_data.items():
            # cash 값을 정수로 변환
            account_info["cash"] = int(account_info["cash"])

            # stocks 값을 정수로 변환
            account_info["stocks"] = {stock: int(quantity) for stock, quantity in account_info["stocks"].items()}

        # 변환된 데이터 저장
        with open('economics/account.json', "w", encoding="utf-8") as account:
            json.dump(account_data, account, indent=4, ensure_ascii=False)

        print("account.json 파일의 cash stocks 값을 성공적으로 정수로 변환했습니다!")

    except Exception as e:
        print(f"오류가 발생했습니다: {e}")

client = discord.Client(intents=intents)

@client.event
async def save_image(attachment):
    if not os.path.exists(folder):
        os.makedirs(folder)

    nowtime = datetime.now()
    save_image_time = f"{str(nowtime.year)}년 {str(nowtime.month)}월 {str(nowtime.day)}일 {str(nowtime.hour)}시 {str(nowtime.minute)}분 {str(nowtime.second)}초"

    # image_url = attachment.url
    image_name = attachment.filename
    image_path = os.path.join(folder, image_name)

    await attachment.save(image_path)
    chatlog = (open('chat_log.txt', 'a'))
    chatlog.write(f"Saved file: {image_name} at {image_path} in {save_image_time}" + '\n')
    chatlog.close()

class MyClient(discord.Client):
    @client.event
    async def on_ready(self):
        # Discord Rich Presence 설정
        activity = discord.Activity(
            type=discord.ActivityType.watching,  # 게임 상태
            name="우리소리골",  # 게임 이름
            state="난타를 사랑하는 쌤",  # 상태 텍스트
            details="오방진장단까지",  # 게임의 상세 내용
            start=time.time(),  # 시작 시간 (현재 시간으로 설정)
            # end 시간 (시작 시간으로부터 1시간 뒤로 설정)
            end=time.time() + 3600,
            large_image="competitive",  # 큰 이미지 (Discord 개발자 포털에서 설정한 이미지 이름)
            small_image="rogue_level_100",  # 작은 이미지 (Discord 개발자 포털에서 설정한 이미지 이름)
            large_text="Competitive",  # 큰 이미지에 텍스트 추가
            small_text="Rogue - Level 100",  # 작은 이미지에 텍스트 추가
            party_id="ae488379-351d-4a4f-ad32-2b9b01c91657",  # 파티 ID
            party_size=523,  # 현재 파티 크기
            party_max=2009,  # 최대 파티 크기
            join_secret="MTI4NzM0OjFpMmhuZToxMjMxMjM="  # 참가 비밀
        )
        await client.change_presence(status=discord.Status.online)
        await client.change_presence(activity=activity)

    @staticmethod
    async def on_message(message):
        global stock_increase_decrease_rate  # 전역 변수 선언
        global earned_income_tax
        global lottery_tax
        global gambling_tax
        global stock_purchase_tax
        global stock_sales_tax
        global transfer_tax
        global basic_tax_rate
        global tax_evasion_fine
        global stock_tax_evasion_fine
        global stock_floor_limit
        global rich_tax_increase_rate
        global standard_for_tax_increase_for_the_wealthy
        global reward

        if message.author.bot:
            return None

        # if message.content.startswith("!test"):
        #     webhook = await message.channel.create_webhook(name="Alert Bot")
        #     await webhook.send("긴급 알림: 서버 점검 예정입니다!")
        #
        #     user = message.mentions[0] if message.mentions else message.author
        #     await message.channel.send(user.avatar.url)
        #
        #
        # user_id = str(message.author.id)  # 유저 ID를 문자열로 변환
        # content_length = len(message.content)
        #
        # # 사용자 데이터 초기화
        # if user_id not in user_data:
        #     user_data[user_id] = {"exp": 0, "level": 1, "messages": 0, "name": message.author.name}
        #
        # # EXP 및 메시지 수 업데이트
        # user_data[user_id]["exp"] += content_length
        # user_data[user_id]["messages"] += 1
        #
        # # 레벨 업 처리
        # if user_data[user_id]["exp"] >= 100000:
        #     user_data[user_id]["level"] += 1
        #     user_data[user_id]["exp"] -= 100000
        #     await message.channel.send(f"🎉 {message.author.name}님이 레벨 {user_data[user_id]['level']}로 올랐습니다!")
        #
        # # JSON 데이터 저장
        # with open(USER_DATA_FILE, "w") as chat_count:
        #     json.dump(user_data, chat_count, indent=4)
        #
        # # XP 상태 출력
        # if message.content == "!내채팅정보":
        #     exp = user_data[user_id]["exp"]
        #     level = user_data[user_id]["level"]
        #     messages = user_data[user_id]["messages"]
        #
        #     # 임베드 생성
        #     embed = discord.Embed(
        #         title=f"{message.author.name}님의 프로필",
        #         description="유저의 현재 상태입니다.",
        #         color=discord.Color.blue()  # 원하는 색상
        #     )
        #     embed.add_field(name="레벨", value=f"{level}", inline=True)
        #     embed.add_field(name="EXP", value=f"{exp}/100000", inline=True)
        #     embed.add_field(name="메시지 수", value=f"{messages}", inline=True)
        #
        #     await message.channel.send(embed=embed)
        #
        # # EXP 랭킹 출력
        # if message.content == "!채팅랭킹":
        #     ranking = sorted(user_data.items(), key=lambda x: x[1]["exp"], reverse=True)
        #     ranking_text = "**EXP 랭킹 (상위 10명):**\n"
        #     for i, (user_id, data) in enumerate(ranking[:10]):
        #         ranking_text += f"{i + 1}. {data['name']} - {data['exp']} EXP\n"
        #
        #     await message.channel.send(ranking_text)

        # if message.content == "!퀴즈":
        #     url = "https://opentdb.com/api.php?amount=1&type=multiple"
        #     async with aiohttp.ClientSession() as session:
        #         async with session.get(url) as response:
        #             data = await response.json()
        #             question = data["results"][0]["question"]
        #             correct = data["results"][0]["correct_answer"]
        #             options = data["results"][0]["incorrect_answers"]
        #             options.append(correct)
        #             import random
        #             random.shuffle(options)
        #
        #             quiz_text = f"**{question}**\n" + "\n".join([f"{i + 1}. {opt}" for i, opt in enumerate(options)])
        #             await message.channel.send(quiz_text)
        #
        #             #유저가 치는 메시지 인식해서 점수 주는 코드 작성 바람
        #             await message.channel.send(f"정답은: **{correct}**")
        #
        # if message.content == "!농담":
        #     url = "https://official-joke-api.appspot.com/random_joke"
        #     async with aiohttp.ClientSession() as session:
        #         async with session.get(url) as response:
        #             data = await response.json()
        #             await message.channel.send(f"{data['setup']} ... {data['punchline']}")
        #
        # if message.content.startswith("!날씨"):
        #     #이것도 오류 수정 해야함
        #     city = message.content.split(" ", 1)[1]
        #     api_key = "YOUR_OPENWEATHER_API_KEY"
        #     url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=kr"
        #
        #     async with aiohttp.ClientSession() as session:
        #         async with session.get(url) as response:
        #             data = await response.json()
        #             if data["cod"] != 200:
        #                 await message.channel.send(f"도시를 찾을 수 없습니다: {city}")
        #                 return
        #
        #             weather = data["weather"][0]["description"]
        #             temp = data["main"]["temp"]
        #             await message.channel.send(f"{city}의 날씨는 {weather}, 현재 온도는 {temp}°C 입니다.")
        #
        # #이건 왜 오류나는거임?
        # if message.content.startswith("!요약"):
        #     text = message.content.split(" ", 1)[1]
        #     url = "https://api.text-summary.com/summarize"
        #     params = {"text": text, "ratio": 0.3}
        #
        #     async with aiohttp.ClientSession() as session:
        #         async with session.post(url, json=params) as response:
        #             summary = await response.json()
        #             await message.channel.send(f"요약된 내용: {summary['summary']}")
        #
        # #하... api
        # if message.content.startswith("!뉴스"):
        #     keyword = message.content.split(" ", 1)[1] if " " in message.content else "최신"
        #     api_key = "YOUR_NEWS_API_KEY"
        #     url = f"https://newsapi.org/v2/everything?q={keyword}&apiKey={api_key}&language=ko"
        #
        #     async with aiohttp.ClientSession() as session:
        #         async with session.get(url) as response:
        #             data = await response.json()
        #             articles = data["articles"][:5]
        #             for article in articles:
        #                 await message.channel.send(f"**{article['title']}**\n{article['url']}")
        #
        # if message.content == "!트렌드":
        #     url = "https://trends.google.com/trends/hottrends/visualize/internal/data"
        #     async with aiohttp.ClientSession() as session:
        #         async with session.get(url) as response:
        #             data = await response.json()
        #             trends = ", ".join(data["united_states"][:5])  # 미국 트렌드
        #             await message.channel.send(f"현재 트렌드: {trends}")
        #
        # if message.content == "!구글트렌드":
        #     url = "https://trends.google.com/trends/hottrends/visualize/internal/data"
        #     async with aiohttp.ClientSession() as session:
        #         async with session.get(url) as response:
        #             if response.status == 200:
        #                 data = await response.json()
        #                 trends = ", ".join(data.get("united_states", [])[:10])  # 미국 트렌드 기준
        #                 await message.channel.send(f"현재 구글 트렌드(미국): {trends}")
        #             else:
        #                 await message.channel.send("구글 트렌드 데이터를 가져올 수 없습니다.")
        #
        # #뭔가 이상한걸 불러옴...
        # if message.content == "!네이버트렌드":
        #     url = "https://www.signal.bz/news"
        #     async with aiohttp.ClientSession() as session:
        #         async with session.get(url) as response:
        #             if response.status == 200:
        #                 data = await response.json()
        #                 trends = [item["keyword"] for item in data["top10"]]
        #                 trends_text = "\n".join([f"{i + 1}. {trend}" for i, trend in enumerate(trends)])
        #                 await message.channel.send(f"네이버 실시간 검색어:\n{trends_text}")
        #             else:
        #                 await message.channel.send("네이버 실시간 검색어 데이터를 가져올 수 없습니다.")
        #
        # #이새끼도 대가리 깨짐
        # if message.content == "!핫뉴스":
        #     url = "https://www.yna.co.kr/theme/topnews"  # 연합뉴스 주요 뉴스 페이지
        #     async with aiohttp.ClientSession() as session:
        #         async with session.get(url) as response:
        #             if response.status == 200:
        #                 html = await response.text()
        #                 soup = bs4.BeautifulSoup(html, "html.parser")
        #                 articles = soup.select(".list-type038 li")[:10]  # 상위 10개 뉴스
        #
        #                 news = []
        #                 for article in articles:
        #                     title = article.select_one("strong").text.strip()
        #                     link = article.select_one("a")["href"]
        #                     news.append(f"**{title}**\n{link}")
        #
        #                 await message.channel.send("\n\n".join(news))
        #             else:
        #                 await message.channel.send("뉴스 데이터를 가져올 수 없습니다.")

        if message.content.startswith("$dmnotice"):
            args = message.content.split()
            if len(args) < 3:
                print("올바른 형식이 아닙니다.")
            else:
                user_id = args[2]
                count =int(args[1])
                msg = input("출력할 말 : ")
                if msg == "" or count == 0:
                    print("빈 칸 입니다. 잠정 기능 중지 처리 되었습니다.")
                else:
                    try:
                        for i in range(count):
                            # 사용자 객체 가져오기
                            user = await client.fetch_user(user_id)

                            # 사용자에게 DM 보내기
                            await user.send(msg)
                            print(f"DM을 {user.name}님에게 성공적으로 보냈습니다.")

                    except discord.NotFound:
                        print("사용자를 찾을 수 없습니다.")
                    except discord.Forbidden:
                        print("이 사용자는 DM을 받을 수 없습니다.")
                    except Exception as e:
                        print(f"DM 전송 중 오류 발생: {e}")

        if message.content.startswith("$notice"):
            args = message.content.split()

            if len(args) < 2:
                print("올바른 형식이 아닙니다.")

            else:
                count = int(args[1])
                msg = input("출력할 말 : ")

                if msg == "" or count == 0:
                    print("빈 칸 입니다. 잠정 기능 중지 처리 되었습니다.")
                # 봇이 속한 모든 서버의 채팅방 찾기
                else:
                    for i in range(count):
                        for guild in client.guilds:
                            for channel in guild.text_channels:
                                try:
                                    # 채팅방에 메시지 보내기
                                    await channel.send(msg)
                                except discord.Forbidden:
                                    # 채팅방에 메시지를 보낼 권한이 없을 경우
                                    print(f"권한이 없어 {channel.name} 채널에 메시지를 보낼 수 없습니다.")
                                except Exception as e:
                                    print(f"오류 발생: {e}")

        if message.content.startswith("!주식그래프"):
            stock_random()

            args = message.content.split()

            if len(args) != 3:
                await message.channel.send("올바른 사용법: `!주식그래프 <거래소> <주식코드>`")
                return

            exchange = args[1]
            stock_name = args[2]

            try:
                # history.json 데이터 읽기
                with open(HISTORY_FILE, "r", encoding="utf-8") as history:
                    history_data = json.load(history)

                # 필터링된 데이터 가져오기
                filtered_data = [
                    item for item in history_data
                    if item["exchange"] == exchange and item["name"] == stock_name
                ]

                if not filtered_data:
                    await message.channel.send("해당 거래소와 주식코드에 대한 데이터가 없습니다.")
                    return

                # 시간과 가격 추출
                from datetime import datetime
                times = [
                    datetime.strptime(item["time"], "%Y-%m-%d %H:%M:%S") for item in filtered_data
                ]
                prices = [item["price"] for item in filtered_data]

                # 그래프 생성
                plt.rc('font', family=font_name)
                plt.figure(figsize=(10, 5))

                # 상승/하락에 따른 색상 변화
                for i in range(1, len(times)):
                    if prices[i] > prices[i - 1]:
                        plt.plot(times[i - 1:i + 1], prices[i - 1:i + 1], color="red", linestyle="-")  # 상승 빨간색
                    else:
                        plt.plot(times[i - 1:i + 1], prices[i - 1:i + 1], color="blue", linestyle="-")  # 하락 파란색

                plt.title(f"{exchange} - {stock_name} 주가 그래프")
                plt.xlabel("시간")
                plt.ylabel("가격 (원)")
                plt.grid(True)

                # 그래프 이미지 저장
                graph_path = "stock_graph.png"
                plt.savefig(graph_path)
                plt.close()

                # Discord에 그래프 전송
                await message.channel.send(file=discord.File(graph_path))

                # 생성된 파일 삭제
                os.remove(graph_path)

            except Exception as e:
                await message.channel.send(f"오류가 발생했습니다: {e}")

        if message.content.startswith("$세율설정"):
            args = message.content.split()
            if len(args) != 3:
                await message.channel.send(
                    "올바른 형식: `$세율설정 <세금 이름> <값>`\n"
                    "설정 가능한 세금: 근로소득세, 복권세금, 도박세금, 매수세금, 매도세금, "
                    "이체세금, 납세율, 탈세벌금, 주식탈세벌금, 주식최소금액, 재벌증세율"
                )
                return

            tax_name = args[1]
            try:
                value = float(args[2])
                if value < 0:
                    await message.channel.send("세금 값은 0 이상의 값이어야 합니다.")
                    return

                if tax_name == "근로소득세":
                    earned_income_tax = value
                elif tax_name == "복권세금":
                    lottery_tax = value
                elif tax_name == "도박세금":
                    gambling_tax = value
                elif tax_name == "매수세금":
                    stock_purchase_tax = value
                elif tax_name == "매도세금":
                    stock_sales_tax = value
                elif tax_name == "이체세금":
                    transfer_tax = value
                elif tax_name == "납세율":
                    basic_tax_rate = value
                elif tax_name == "탈세벌금":
                    tax_evasion_fine = value
                elif tax_name == "주식탈세벌금":
                    stock_tax_evasion_fine = value
                elif tax_name == "주식최소금액":
                    stock_floor_limit = value
                elif tax_name == "재벌증세율":
                    rich_tax_increase_rate = value
                elif tax_name == "재벌증세율기준":
                    standard_for_tax_increase_for_the_wealthy = value
                else:
                    await message.channel.send("올바른 세금 이름을 입력하세요.")
                    return

                await message.channel.send(f"{tax_name}이(가) {value}로 설정되었습니다.")

            except ValueError:
                await message.channel.send("값은 숫자여야 합니다.")

        if message.content.startswith("$일급설정"):
            args = message.content.split()
            value = args[1]
            if len(args) != 2:
                await message.channel.send("올바른 형식: `일급설정 <값>`")
                return

            await message.channel.send(f"일급이 {value}로 설정되었습니다.")

        if message.content.startswith("forge"):
            args = message.content.split()
            count = args[1]
            if len(args) != 2:
                await message.channel.send("형식이 바르지 않습니다.")
            else:
                for i in range(int(count)):
                    stock_random()
                    did = i + 1
                    print(f"{count}중 {did}만큼 돌렸습니다.")
            await message.channel.send("Complete!")

        if message.content.startswith("!일당정기소득보기"):
            await message.channel.send(
                f"**현재 일급 설정:** {reward}"
            )

        if message.content == "!세율":
            await message.channel.send(
                f"**현재 세금 설정:**\n"
                f"근로소득세: {earned_income_tax}\n"
                f"복권세금: {lottery_tax}\n"
                f"도박세금: {gambling_tax}\n"
                f"매수세금: {stock_purchase_tax}\n"
                f"매도세금: {stock_sales_tax}\n"
                f"이체세금: {transfer_tax}\n"
                f"납세율: {basic_tax_rate}\n"
                f"탈세벌금: {tax_evasion_fine}\n"
                f"주식탈세벌금: {stock_tax_evasion_fine}\n"
                f"주식최소금액: {stock_floor_limit}\n"
                f"재벌증세율: {rich_tax_increase_rate}\n"
                f"재벌증세율기준: {standard_for_tax_increase_for_the_wealthy}"
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
                    stock_increase_decrease_rate = value
                    await message.channel.send(f"주식 확률이 {stock_increase_decrease_rate}로 설정되었습니다.")
                else:
                    await message.channel.send("확률 값은 0과 1 사이의 소수여야 합니다.")
            except ValueError:
                await message.channel.send("확률 값은 숫자여야 합니다.")

        # '!get_probability' 명령어 처리
        if message.content == "$주식등락률보기":
            await message.channel.send(f"현재 주식 확률은 {stock_increase_decrease_rate}입니다.")

        if message.content.startswith("!계좌개설"):
            user_id = str(message.author.id)
            account = os.path.join(FOLDER, "account.json")

            with open(account, "r+", encoding="utf-8") as account:
                data = json.load(account)
                if user_id in data:
                    await message.channel.send("이미 계좌가 존재합니다.")
                    return
                data[user_id] = {"cash": 2100000, "stocks": {}}
                account.seek(0)
                json.dump(data, account, indent=4, ensure_ascii=False)

            await message.channel.send("계좌가 성공적으로 개설되었습니다.")

        if message.content.startswith("!일급"):
            user_id = str(message.author.id)
            daily_path = os.path.join(FOLDER, "daily_reward.json")
            account_path = os.path.join(FOLDER, "account.json")

            with open(daily_path, "r+", encoding="utf-8") as daily:
                daily_data = json.load(daily)
                import datetime
                todaydate = datetime.datetime.now().strftime("%Y-%m-%d")

                if any(record["user"] == user_id and record["date"] == todaydate for record in daily_data):
                    await message.channel.send("이미 오늘의 일급을 받았습니다.")
                    return

                daily_data.append({"user": user_id, "date": todaydate})
                daily.seek(0)
                json.dump(daily_data, daily, indent=4, ensure_ascii=False)

            with open(account_path, "r+", encoding="utf-8") as account:
                account_data = json.load(account)
                if user_id not in account_data:
                    await message.channel.send("계좌를 먼저 개설해주세요.")
                    return

                account_data[user_id]["cash"] += reward
                account.seek(0)
                json.dump(account_data, account, indent=4, ensure_ascii=False)

            await message.channel.send(f"{reward}원이 지급되었습니다.")

            # 납세 처리: 현금과 주식 확인 및 납세 진행
            account_path = os.path.join(FOLDER, "account.json")
            with open(account_path, "r", encoding="utf-8") as account:
                account_data = json.load(account)

            if user_id not in account_data:
                await message.channel.send("계좌가 존재하지 않습니다. 계좌를 개설해주세요.")
            else:
                user_account = account_data[user_id]
                cash_balance = user_account["cash"]

                tax_amount = cash_balance * earned_income_tax  # 소득세 10% 세금

                # 현금 차감
                user_account["cash"] -= tax_amount

                # 로또 기금에 세금 금액 추가
                lotto_path = os.path.join(FOLDER, "lotto.json")
                if not os.path.exists(lotto_path):
                    # 로또 파일이 없으면 기본값을 설정하여 생성
                    lotto_data = {"cash": 0, "stocks": {}}
                else:
                    try:
                        with open(lotto_path, "r", encoding="utf-8") as lotto:
                            lotto_data = json.load(lotto)
                    except json.JSONDecodeError:
                        # JSON 오류가 발생하면 기본값으로 초기화
                        lotto_data = {"cash": 0, "stocks": {}}

                lotto_data["cash"] += tax_amount  # 세금 금액을 로또 기금에 추가

                # 로또 파일에 업데이트된 데이터 저장
                with open(lotto_path, "w", encoding="utf-8") as lotto:
                    json.dump(lotto_data, lotto, indent=4, ensure_ascii=False)

                # 계좌 정보 업데이트: 차감된 현금과 주식 정보 저장
                with open(account_path, "w", encoding="utf-8") as account:
                    json.dump(account_data, account, ensure_ascii=False, indent=4)

        if message.content.startswith("!납세"):
            # tax_person.json 파일 확인
            if os.path.exists(TAX_PERSON_FILE):
                with open(TAX_PERSON_FILE, 'r', encoding="utf-8") as tax_person:
                    tax_person_data = json.load(tax_person)
            else:
                tax_person_data = {}

            import datetime
            today_date = datetime.datetime.now().strftime("%Y-%m-%d")  # 오늘 날짜

            # 이미 납세한 경우
            user_id = str(message.author.id)
            if user_id in tax_person_data and tax_person_data[user_id] == today_date:
                await message.channel.send("오늘은 이미 납세를 하셨습니다. 내일 다시 시도해 주세요.")
            else:
                # 납세 처리: 현금과 주식 확인 및 납세 진행
                account_path = os.path.join(FOLDER, "account.json")
                with open(account_path, "r", encoding="utf-8") as account:
                    account_data = json.load(account)

                if user_id not in account_data:
                    await message.channel.send("계좌가 존재하지 않습니다. 계좌를 개설해주세요.")
                else:
                    user_account = account_data[user_id]
                    cash_balance = user_account["cash"]

                    tax_amount = cash_balance * basic_tax_rate  # 3% 세금

                    # 현금이 부족하면 납세할 수 없음
                    if cash_balance < tax_amount:
                        await message.channel.send("납세를 위한 현금이 부족합니다.")
                    else:
                        hundred_million_tax_amount = cash_balance * rich_tax_increase_rate

                        if cash_balance >= standard_for_tax_increase_for_the_wealthy:
                            user_account["cash"] -= hundred_million_tax_amount

                            # 로또 기금에 세금 금액 추가
                            lotto_path = os.path.join(FOLDER, "lotto.json")
                            if not os.path.exists(lotto_path):
                                # 로또 파일이 없으면 기본값을 설정하여 생성
                                lotto_data = {"cash": 0, "stocks": {}}
                            else:
                                try:
                                    with open(lotto_path, "r", encoding="utf-8") as lotto:
                                        lotto_data = json.load(lotto)
                                except json.JSONDecodeError:
                                    # JSON 오류가 발생하면 기본값으로 초기화
                                    lotto_data = {"cash": 0, "stocks": {}}

                            lotto_data["cash"] += hundred_million_tax_amount  # 세금 금액을 로또 기금에 추가

                            # 로또 파일에 업데이트된 데이터 저장
                            with open(lotto_path, "w", encoding="utf-8") as lotto:
                                json.dump(lotto_data, lotto, indent=4, ensure_ascii=False)

                            # 계좌 정보 업데이트: 차감된 현금 저장
                            with open(account_path, "w", encoding="utf-8") as account:
                                json.dump(account_data, account, ensure_ascii=False, indent=4)

                            # 납세 기록 추가
                            tax_person_data[user_id] = today_date
                            with open(TAX_PERSON_FILE, 'w', encoding="utf-8") as tax_person:
                                json.dump(tax_person_data, tax_person, ensure_ascii=False, indent=4)

                            await message.channel.send(f"납세가 완료되었습니다. {hundred_million_tax_amount} 원이 차감되었습니다.")

                        else:
                            user_account["cash"] -= tax_amount

                            # 로또 기금에 세금 금액 추가
                            lotto_path = os.path.join(FOLDER, "lotto.json")
                            if not os.path.exists(lotto_path):
                                # 로또 파일이 없으면 기본값을 설정하여 생성
                                lotto_data = {"cash": 0, "stocks": {}}
                            else:
                                try:
                                    with open(lotto_path, "r", encoding="utf-8") as lotto:
                                        lotto_data = json.load(lotto)
                                except json.JSONDecodeError:
                                    # JSON 오류가 발생하면 기본값으로 초기화
                                    lotto_data = {"cash": 0, "stocks": {}}

                            lotto_data["cash"] += tax_amount  # 세금 금액을 로또 기금에 추가

                            # 로또 파일에 업데이트된 데이터 저장
                            with open(lotto_path, "w", encoding="utf-8") as lotto:
                                json.dump(lotto_data, lotto, indent=4, ensure_ascii=False)

                            # 계좌 정보 업데이트: 차감된 현금 저장
                            with open(account_path, "w", encoding="utf-8") as account:
                                json.dump(account_data, account, ensure_ascii=False, indent=4)

                            # 납세 기록 추가
                            tax_person_data[user_id] = today_date
                            with open(TAX_PERSON_FILE, 'w', encoding="utf-8") as tax_person:
                                json.dump(tax_person_data, tax_person, ensure_ascii=False, indent=4)

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
                with open(account_path, "r+", encoding="utf-8") as account:
                    account_data = json.load(account)

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
                    account.seek(0)
                    json.dump(account_data, account, indent=4, ensure_ascii=False)
                    account.truncate()

                # lotto.json 파일 읽기 및 업데이트
                with open(lotto_path, "r+", encoding="utf-8") as lotto:
                    lotto_data = json.load(lotto)

                    # 기부금 추가
                    lotto_data["cash"] += donation_amount
                    lotto.seek(0)
                    json.dump(lotto_data, lotto, indent=4, ensure_ascii=False)
                    lotto.truncate()

                # 완료 메시지
                await message.channel.send(f"{donation_amount}원이 성공적으로 기부되었습니다!")

            except Exception as e:
                await message.channel.send(f"기부 처리 중 오류가 발생했습니다: {e}")

        if message.content.startswith("!로또참여"):
            user_id = str(message.author.id)
            account_path = os.path.join(FOLDER, "account.json")
            lotto_player_path = os.path.join(FOLDER, "lotto_player.json")

            with open(account_path, "r+", encoding="utf-8") as account:
                account_data = json.load(account)
                if user_id not in account_data:
                    await message.channel.send("계좌를 먼저 개설해주세요.")
                    return

                if account_data[user_id]["cash"] < 100000:
                    await message.channel.send("로또에 참가하려면 최소 10만 원의 현금이 필요합니다.")
                    return

                account_data[user_id]["cash"] -= 100000
                account.seek(0)
                json.dump(account_data, account, indent=4, ensure_ascii=False)

            with open(lotto_player_path, "r+", encoding="utf-8") as lotto_player:
                lotto_players = json.load(lotto_player)
                if user_id in lotto_players:
                    await message.channel.send("이미 로또에 참가하셨습니다.")
                    return

                lotto_players.append(user_id)
                lotto_player.seek(0)
                json.dump(lotto_players, lotto_player, indent=4, ensure_ascii=False)

            await message.channel.send("로또에 참가하였습니다. 행운을 빕니다!")

            user_id = str(message.author.id)  # 유저 ID 가져오기

            # 납세 처리: 현금과 주식 확인 및 납세 진행
            account_path = os.path.join(FOLDER, "account.json")
            with open(account_path, "r", encoding="utf-8") as account:
                account_data = json.load(account)

            if user_id not in account_data:
                await message.channel.send("계좌가 존재하지 않습니다. 계좌를 개설해주세요.")
            else:
                user_account = account_data[user_id]
                cash_balance = user_account["cash"]

                tax_amount = cash_balance * lottery_tax  # 소득세 10% 세금

                # 현금 차감
                user_account["cash"] -= tax_amount

                # 로또 기금에 세금 금액 추가
                lotto_path = os.path.join(FOLDER, "lotto.json")
                if not os.path.exists(lotto_path):
                    # 로또 파일이 없으면 기본값을 설정하여 생성
                    lotto_data = {"cash": 0, "stocks": {}}
                else:
                    try:
                        with open(lotto_path, "r", encoding="utf-8") as lotto:
                            lotto_data = json.load(lotto)
                    except json.JSONDecodeError:
                        # JSON 오류가 발생하면 기본값으로 초기화
                        lotto_data = {"cash": 0, "stocks": {}}

                lotto_data["cash"] += tax_amount  # 세금 금액을 로또 기금에 추가

                # 로또 파일에 업데이트된 데이터 저장
                with open(lotto_path, "w", encoding="utf-8") as lotto:
                    json.dump(lotto_data, lotto, indent=4, ensure_ascii=False)

                # 계좌 정보 업데이트: 차감된 현금과 주식 정보 저장
                with open(account_path, "w", encoding="utf-8") as account:
                    json.dump(account_data, account, ensure_ascii=False, indent=4)

        if message.content.startswith("$tax check"):
            account_path = os.path.join(FOLDER, "account.json")
            tax_path = os.path.join(FOLDER, "tax.json")
            lotto_path = os.path.join(FOLDER, "lotto.json")

            with open(account_path, "r+", encoding="utf-8") as account:
                account_data = json.load(account)

            with open(tax_path, "r+", encoding="utf-8") as tax:
                tax_data = json.load(tax)

            with open(lotto_path, "r+", encoding="utf-8") as lotto:
                lotto_data = json.load(lotto)

            penalized_users = []
            for user_id, account in account_data.items():
                if user_id not in tax_data and account["cash"] >= 100000:
                    penalty_cash = int(account["cash"] * tax_evasion_fine)
                    penalty_stocks = {stock: int(amount * stock_tax_evasion_fine) for stock, amount in account["stocks"].items()}

                    account["cash"] -= penalty_cash
                    for stock, amount in penalty_stocks.items():
                        account["stocks"][stock] -= amount
                        lotto_data["stocks"][stock] = lotto_data["stocks"].get(stock, 0) + amount

                    lotto_data["cash"] += penalty_cash
                    penalized_users.append(user_id)

            with open(account_path, "w", encoding="utf-8") as account:
                json.dump(account_data, account, indent=4, ensure_ascii=False)

            with open(lotto_path, "w", encoding="utf-8") as lotto:
                json.dump(lotto_data, lotto, indent=4, ensure_ascii=False)

            tax_data.clear()
            with open(tax_path, "w", encoding="utf-8") as tax:
                json.dump(tax_data, tax, indent=4, ensure_ascii=False)

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
                with open(lotto_player_path, 'r', encoding="utf-8") as lotto_player:
                    lotto_player_data = json.load(lotto_player)
            else:
                lotto_player_data = []

            if not lotto_player_data:
                await message.channel.send("로또에 참여한 유저가 없습니다.")
                return

            # lotto.json에서 기금 정보 확인
            if os.path.exists(lotto_path):
                with open(lotto_path, 'r', encoding="utf-8") as lotto:
                    lotto_data = json.load(lotto)
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
            with open(account_path, 'r', encoding="utf-8") as account:
                account_data = json.load(account)

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
            with open(account_path, 'w', encoding="utf-8") as account:
                json.dump(account_data, account, ensure_ascii=False, indent=4)

            # 로또 기금 정보 업데이트
            with open(lotto_path, 'w', encoding="utf-8") as lotto:
                json.dump({"cash": lotto_cash, "stocks": lotto_stocks}, lotto, ensure_ascii=False, indent=4)

            # 로또 참여자 목록에서 당첨자 제외 (선택 사항)
            # lotto_player_data.remove(winner_id)
            # with open(lotto_player_path, 'w', encoding="utf-8") as f:
            #     json.dump(lotto_player_data, f, ensure_ascii=False, indent=4)

            await message.channel.send(f"축하합니다! {winner_id}님이 로또에 당첨되었습니다!")

        if message.content.startswith("!bet"):
            stock_random()

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
                with open(account_path, "w", encoding="utf-8") as account:
                    json.dump(FILES["account.json"], account, indent=4, ensure_ascii=False)

            with open(account_path, "r", encoding="utf-8") as account:
                try:
                    account_data = json.load(account)
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
                with open(gamble_config_path, "w", encoding="utf-8") as gamble_config_file:
                    json.dump(FILES["gamble_config.json"], gamble_config_file, indent=4, ensure_ascii=False)

            with open(gamble_config_path, "r", encoding="utf-8") as gamble_config_file:
                try:
                    gamble_config = json.load(gamble_config_file)
                except json.JSONDecodeError:
                    gamble_config = FILES["gamble_config.json"]

            probability = gamble_config.get("probability", 50)

            # gamble_reward.json 처리
            if not os.path.exists(gamble_reward_path):
                with open(gamble_reward_path, "w", encoding="utf-8") as gamble_reward_file:
                    json.dump(FILES["gamble_reward.json"], gamble_reward_file, indent=4, ensure_ascii=False)

            with open(gamble_reward_path, "r", encoding="utf-8") as gamble_reward_file:
                try:
                    reward_config = json.load(gamble_reward_file)
                except json.JSONDecodeError:
                    reward_config = FILES["gamble_reward.json"]

            multiplier = reward_config.get("multiplier", 2)

            # lotto.json 처리
            if not os.path.exists(lotto_path):
                with open(lotto_path, "w", encoding="utf-8") as lotto:
                    json.dump(FILES["lotto.json"], lotto, indent=4, ensure_ascii=False)

            with open(lotto_path, "r", encoding="utf-8") as lotto:
                try:
                    lotto_data = json.load(lotto)
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
            with open(account_path, "w", encoding="utf-8") as account:
                json.dump(account_data, account, indent=4, ensure_ascii=False)

            with open(lotto_path, "w", encoding="utf-8") as lotto:
                json.dump(lotto_data, lotto, indent=4, ensure_ascii=False)

            await message.channel.send(result)

            # 납세 처리: 현금과 주식 확인 및 납세 진행
            account_path = os.path.join(FOLDER, "account.json")
            with open(account_path, "r", encoding="utf-8") as account:
                account_data = json.load(account)

            if user_id not in account_data:
                await message.channel.send("계좌가 존재하지 않습니다. 계좌를 개설해주세요.")
            else:
                user_account = account_data[user_id]
                cash_balance = user_account["cash"]

                tax_amount = cash_balance * gambling_tax  # 소득세 10% 세금

                # 현금 차감
                user_account["cash"] -= tax_amount

                # 로또 기금에 세금 금액 추가
                lotto_path = os.path.join(FOLDER, "lotto.json")
                if not os.path.exists(lotto_path):
                    # 로또 파일이 없으면 기본값을 설정하여 생성
                    lotto_data = {"cash": 0, "stocks": {}}
                else:
                    try:
                        with open(lotto_path, "r", encoding="utf-8") as lotto:
                            lotto_data = json.load(lotto)
                    except json.JSONDecodeError:
                        # JSON 오류가 발생하면 기본값으로 초기화
                        lotto_data = {"cash": 0, "stocks": {}}

                lotto_data["cash"] += tax_amount  # 세금 금액을 로또 기금에 추가

                # 로또 파일에 업데이트된 데이터 저장
                with open(lotto_path, "w", encoding="utf-8") as lotto:
                    json.dump(lotto_data, lotto, indent=4, ensure_ascii=False)

                # 계좌 정보 업데이트: 차감된 현금과 주식 정보 저장
                with open(account_path, "w", encoding="utf-8") as account:
                    json.dump(account_data, account, ensure_ascii=False, indent=4)

        # !매수 명령어 처리
        elif message.content.startswith("!매수"):
            price_fix("KDJ", "000020", 523)

            args = message.content.split()[1:]  # 명령어 인자 분리
            user_id = str(message.author.id)  # 유저 ID 가져오기

            # 계좌 정보 불러오기
            with open(ACCOUNT_FILE, 'r') as account:
                account_data = json.load(account)

            # 주식 정보 불러오기
            with open(STOCK_FILE, 'r') as stock:
                stock_data = json.load(stock)

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
            with open(ACCOUNT_FILE, 'w') as account:
                json.dump(account_data, account, indent=4)

            user_id = str(message.author.id)  # 유저 ID 가져오기

            # 납세 처리: 현금과 주식 확인 및 납세 진행
            account_path = os.path.join(FOLDER, "account.json")
            with open(account_path, "r", encoding="utf-8") as account:
                account_data = json.load(account)

            if user_id not in account_data:
                await message.channel.send("계좌가 존재하지 않습니다. 계좌를 개설해주세요.")
            else:
                user_account = account_data[user_id]
                cash_balance = user_account["cash"]

                tax_amount = cash_balance * stock_purchase_tax  # 소득세 10% 세금

                # 현금 차감
                user_account["cash"] -= tax_amount

                # 로또 기금에 세금 금액 추가
                lotto_path = os.path.join(FOLDER, "lotto.json")
                if not os.path.exists(lotto_path):
                    # 로또 파일이 없으면 기본값을 설정하여 생성
                    lotto_data = {"cash": 0, "stocks": {}}
                else:
                    try:
                        with open(lotto_path, "r", encoding="utf-8") as lotto:
                            lotto_data = json.load(lotto)
                    except json.JSONDecodeError:
                        # JSON 오류가 발생하면 기본값으로 초기화
                        lotto_data = {"cash": 0, "stocks": {}}

                lotto_data["cash"] += tax_amount  # 세금 금액을 로또 기금에 추가

                # 로또 파일에 업데이트된 데이터 저장
                with open(lotto_path, "w", encoding="utf-8") as lotto:
                    json.dump(lotto_data, lotto, indent=4, ensure_ascii=False)

                # 계좌 정보 업데이트: 차감된 현금과 주식 정보 저장
                with open(account_path, "w", encoding="utf-8") as lotto:
                    json.dump(account_data, lotto, ensure_ascii=False, indent=4)

            await message.channel.send(f"{quantity}개의 {stock_code} 주식을 매수했습니다. 잔액: {account_data[user_id]['cash']} 원")
            stock_random()

        # !매도 명령어 처리
        elif message.content.startswith("!매도"):
            price_fix("KDJ", "000020", 523)

            args = message.content.split()[1:]  # 명령어 인자 분리
            user_id = str(message.author.id)  # 유저 ID 가져오기

            # 계좌 정보 불러오기
            with open(ACCOUNT_FILE, 'r') as account:
                account_data = json.load(account)

            # 주식 정보 불러오기
            with open(STOCK_FILE, 'r') as stock:
                stock_data = json.load(stock)

            # 유저가 계좌를 가지고 있는지 확인
            if user_id not in account_data:
                await message.channel.send("먼저 계좌를 개설하세요!")
                return

            # 필요한 인자 받기 (거래소, 주식 코드, 수량)
            if len(args) != 3:
                await message.channel.send("사용법: !매도 <거래소> <주식코드> <수량>")
                return

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
            with open(ACCOUNT_FILE, 'w') as account:
                json.dump(account_data, account, indent=4)

            user_id = str(message.author.id)  # 유저 ID 가져오기

            # 납세 처리: 현금과 주식 확인 및 납세 진행
            account_path = os.path.join(FOLDER, "account.json")
            with open(account_path, "r", encoding="utf-8") as account:
                account_data = json.load(account)

            if user_id not in account_data:
                await message.channel.send("계좌가 존재하지 않습니다. 계좌를 개설해주세요.")
            else:
                user_account = account_data[user_id]
                cash_balance = user_account["cash"]

                tax_amount = cash_balance * stock_sales_tax # 소득세 10% 세금

                # 현금 차감
                user_account["cash"] -= tax_amount

                # 로또 기금에 세금 금액 추가
                lotto_path = os.path.join(FOLDER, "lotto.json")
                if not os.path.exists(lotto_path):
                    # 로또 파일이 없으면 기본값을 설정하여 생성
                    lotto_data = {"cash": 0, "stocks": {}}
                else:
                    try:
                        with open(lotto_path, "r", encoding="utf-8") as lotto:
                            lotto_data = json.load(lotto)
                    except json.JSONDecodeError:
                        # JSON 오류가 발생하면 기본값으로 초기화
                        lotto_data = {"cash": 0, "stocks": {}}

                lotto_data["cash"] += tax_amount  # 세금 금액을 로또 기금에 추가

                # 로또 파일에 업데이트된 데이터 저장
                with open(lotto_path, "w", encoding="utf-8") as lotto:
                    json.dump(lotto_data, lotto, indent=4, ensure_ascii=False)

                # 계좌 정보 업데이트: 차감된 현금과 주식 정보 저장
                with open(account_path, "w", encoding="utf-8") as account:
                    json.dump(account_data, account, ensure_ascii=False, indent=4)

            await message.channel.send(f"{quantity}개의 {stock_code} 주식을 매도했습니다. 잔액: {account_data[user_id]['cash']} 원")
            stock_random()


        if message.content.startswith("!주식기록"):
            stock_random()

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

                with open(history_path, "r", encoding="utf-8") as history:
                    history_data = json.load(history)

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
            price_fix("KDJ", "000020", 523)

            args = message.content.split()
            if len(args) != 3:
                await message.channel.send("올바른 형식: `!주식정보 <거래소> <주식코드>`")
                return

            stock_code = args[2]
            stock_path = os.path.join(FOLDER, "stock.json")

            with open(stock_path, "r", encoding="utf-8") as stock:
                stock_data = json.load(stock)

            if stock_code not in stock_data:
                await message.channel.send("해당 주식이 존재하지 않습니다.")
                return

            stock_info = stock_data[stock_code]
            embed = discord.Embed(title=f"📄 주식 정보: {stock_info['name']} ({stock_code})", color=0x0000FF)
            embed.add_field(name="거래소", value=f"{stock_info['nation']}의 {stock_info['exchange']}", inline=False)
            embed.add_field(name="가격", value=f"{stock_info['price']}원", inline=False)
            embed.add_field(name="발행 주식 수", value=f"{stock_info['total_shares']}주", inline=False)
            embed.add_field(name="거래 가능 주식 수", value=f"{stock_info['tradable_shares']}주", inline=False)

            await message.channel.send(embed=embed)

        if message.content.startswith("!주식기록"):
            stock_random()

            args = message.content.split()
            if len(args) != 3:
                await message.channel.send("올바른 형식: `!주식기록 <거래소> <주식코드>`")
                return

            exchange, stock_code = args[1], args[2]
            history_path = os.path.join(FOLDER, "history.json")
            stock_path = os.path.join(FOLDER, "stock.json")

            # 주식 존재 여부 확인
            with open(stock_path, "r", encoding="utf-8") as stock:
                stock_data = json.load(stock)

            if stock_code not in stock_data or stock_data[stock_code]["exchange"] != exchange:
                await message.channel.send("해당 주식이 존재하지 않습니다.")
                return

            # 변동 기록 조회
            try:
                with open(history_path, "r", encoding="utf-8") as history:
                    history_data = json.load(history)
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
                with open(stock_path, "r", encoding="utf-8") as stock:
                    stock_data = json.load(stock)

                if not stock_data:
                    await message.channel.send("등록된 주식이 없습니다.")
                    return

                # history.json 읽기 (없으면 초기화)
                if not os.path.exists(history_path):
                    with open(history_path, "w", encoding="utf-8") as history:
                        json.dump([], history, indent=4, ensure_ascii=False)

                with open(history_path, "r", encoding="utf-8") as history:
                    history_data = json.load(history)

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
                with open(stock_path, "w", encoding="utf-8") as stock:
                    json.dump(stock_data, stock, indent=4, ensure_ascii=False)

                # history.json 업데이트
                with open(history_path, "w", encoding="utf-8") as history:
                    json.dump(history_data, history, indent=4, ensure_ascii=False)

                await message.channel.send("모든 주식의 가격이 랜덤하게 변경되고, 변경 이력이 저장되었습니다!")

            except Exception as e:
                await message.channel.send(f"주식 가격 변경 중 오류가 발생했습니다: {e}")

        if message.content == "$reset_daily_rewards":
            # daily_reward.json 파일 경로
            daily_reward_path = os.path.join(FOLDER, "daily_reward.json")

            # daily_reward.json 파일 초기화
            try:
                with open(daily_reward_path, "w", encoding="utf-8") as daily_reward:
                    json.dump([], daily_reward, ensure_ascii=False, indent=4)
                await message.channel.send("Daily reward 기록이 초기화되었습니다!")
            except Exception as e:
                await message.channel.send(f"초기화에 실패했습니다: {e}")

        if message.content == "$reset_tax_person":
            # tax_person.json 파일 경로
            tax_person_path = os.path.join(FOLDER, "tax_person.json")

            # tax_person.json 파일 초기화
            try:
                with open(tax_person_path, "w", encoding="utf-8") as tax_person:
                    json.dump({}, tax_person, ensure_ascii=False, indent=4)
                await message.channel.send("tax person 기록이 초기화되었습니다!")
            except Exception as e:
                await message.channel.send(f"초기화에 실패했습니다: {e}")

        if message.content == "$reset_lotto_player":
            # lotto_player.json 파일 경로
            lotto_player_path = os.path.join(FOLDER, "lotto_player.json")

            # lotto_player.json 파일 초기화
            try:
                with open(lotto_player_path, "w", encoding="utf-8") as lotto_player:
                    json.dump([], lotto_player, ensure_ascii=False, indent=4)
                await message.channel.send("lotto player 기록이 초기화되었습니다!")
            except Exception as e:
                await message.channel.send(f"초기화에 실패했습니다: {e}")

        if message.content == "$reset_history":
            # history.json 파일 경로
            history_path = os.path.join(FOLDER, "history.json")

            # history.json 파일 초기화
            try:
                with open(history_path, "w", encoding="utf-8") as history:
                    json.dump([], history, ensure_ascii=False, indent=4)
                await message.channel.send("주식기록이 초기화되었습니다!")
            except Exception as e:
                await message.channel.send(f"초기화에 실패했습니다: {e}")

        if message.content.startswith("$stock publish"):
            args = message.content.split()
            if len(args) != 9:
                await message.channel.send("올바른 형식: `$stock publish <주식명> <국가> <거래소> <카테고리> <주당 가격> <발행 주식 수> <거래 가능한 비율>`")
                return

            stock_name = args[2]
            nation = args[3]
            exchange = args[4]
            category = args[5]
            price = int(args[6])
            total_shares = int(args[7])
            tradable_ratio = float(args[8])

            stock_path = os.path.join(FOLDER, "stock.json")

            with open(stock_path, "r", encoding="utf-8") as stock:
                stock_data = json.load(stock)

            new_stock_code = f"{len(stock_data):06d}"

            stock_data[new_stock_code] = {
                "name": stock_name,
                "nation": nation,
                "exchange": exchange,
                "category": category,
                "price": price,
                "total_shares": total_shares,
                "tradable_shares": total_shares * (tradable_ratio/100)
            }

            with open(stock_path, "w", encoding="utf-8") as stock:
                json.dump(stock_data, stock, ensure_ascii=False, indent=4)

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

            with open(stock_path, "r", encoding="utf-8") as stock:
                stock_data = json.load(stock)

            if stock_code not in stock_data or stock_data[stock_code]["exchange"] != exchange:
                await message.channel.send("해당 주식이 존재하지 않거나 거래소가 맞지 않습니다.")
                return

            del stock_data[stock_code]

            with open(stock_path, "w", encoding="utf-8") as stock:
                json.dump(stock_data, stock, ensure_ascii=False, indent=4)

            with open(account_path, "r", encoding="utf-8") as account:
                account_data = json.load(account)

            for user_id, account in account_data.items():
                if stock_code in account['stocks']:
                    del account['stocks'][stock_code]

            with open(account_path, "w", encoding="utf-8") as account:
                json.dump(account_data, account, ensure_ascii=False, indent=4)

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

            with open(stock_path, "r", encoding="utf-8") as stock:
                stock_data = json.load(stock)

            if stock_code not in stock_data or stock_data[stock_code]["exchange"] != exchange:
                await message.channel.send("해당 주식이 존재하지 않습니다.")
                return

            stock_data[stock_code]["price"] += price_increase

            with open(stock_path, "w", encoding="utf-8") as stock:
                json.dump(stock_data, stock, ensure_ascii=False, indent=4)

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

            with open(stock_path, "r", encoding="utf-8") as stock:
                stock_data = json.load(stock)

            if stock_code not in stock_data or stock_data[stock_code]["exchange"] != exchange:
                await message.channel.send("해당 주식이 존재하지 않습니다.")
                return

            stock_data[stock_code]["price"] -= price_decrease

            with open(stock_path, "w", encoding="utf-8") as stock:
                json.dump(stock_data, stock, ensure_ascii=False, indent=4)

            await message.channel.send(f"{stock_code}의 주식 가격이 {price_decrease}만큼 감소했습니다.")

        if message.content.startswith("$stock set"):
            args = message.content.split()
            if len(args) != 5:
                await message.channel.send("올바른 형식: `$stock set <거래소> <주식코드> <새로운 가격>`")
                return

            exchange = args[2]
            stock_number = args[3]
            new_price = int(args[4])

            stock_path = os.path.join(FOLDER, "stock.json")

            with open(stock_path, "r", encoding="utf-8") as stock:
                stock_data = json.load(stock)

            if stock_number not in stock_data or stock_data[stock_number]["exchange"] != exchange:
                await message.channel.send("해당 주식이 존재하지 않습니다.")
                return

            stock_data[stock_number]["price"] = new_price

            with open(stock_path, "w", encoding="utf-8") as stock:
                json.dump(stock_data, stock, ensure_ascii=False, indent=4)

            await message.channel.send(f"{stock_number}의 주식 가격이 {new_price}로 설정되었습니다.")

        if message.content.startswith("$stock split"):
            args = message.content.split()
            if len(args) != 5:
                await message.channel.send("올바른 형식: `$stock split <거래소> <주식코드> <분할 비율>`")
                return

            exchange = args[2]
            stock_code = args[3]
            split_ratio = int(args[4])

            stock_path = os.path.join(FOLDER, "stock.json")

            with open(stock_path, "r", encoding="utf-8") as stock:
                stock_data = json.load(stock)

            if stock_code not in stock_data or stock_data[stock_code]["exchange"] != exchange:
                await message.channel.send("해당 주식이 존재하지 않습니다.")
                return

            stock_data[stock_code]["total_shares"] *= split_ratio
            stock_data[stock_code]["tradable_shares"] *= split_ratio

            with open(stock_path, "w", encoding="utf-8") as stock:
                json.dump(stock_data, stock, ensure_ascii=False, indent=4)

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

            with open(stock_path, "r", encoding="utf-8") as stock:
                stock_data = json.load(stock)

            if stock_code not in stock_data or stock_data[stock_code]["exchange"] != exchange:
                await message.channel.send("해당 주식이 존재하지 않습니다.")
                return

            stock_data[stock_code]["total_shares"] //= merge_ratio

        # !이체 명령어 처리
        if message.content.startswith("!이체"):

            args = message.content.split()[1:]  # 명령어 인자 분리
            user_id = str(message.author.id)  # 유저 ID 가져오기

            # 계좌 정보 불러오기
            with open(ACCOUNT_FILE, 'r') as account:
                account_data = json.load(account)

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
            with open(ACCOUNT_FILE, 'w') as account:
                json.dump(account_data, account, indent=4)

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
            with open(account_path, "r", encoding="utf-8") as account:
                account_data = json.load(account)

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
            with open(account_path, "w", encoding="utf-8") as account:
                json.dump(account_data, account, ensure_ascii=False, indent=4)

        # !지갑 명령어 처리
        if message.content.startswith("!지갑"):
            stock_random()

            user_id = str(message.author.id)

            # 계좌 정보 로딩
            account_path = os.path.join(FOLDER, "account.json")
            with open(account_path, "r", encoding="utf-8") as account:
                account_data = json.load(account)

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
            with open(STOCK_FILE, "r", encoding="utf-8") as stock:
                stock_data = json.load(stock)

            for stock_key, quantity in stocks.items():
                stock_info = stock_data.get(stock_key)
                if stock_info:
                    exchange = stock_info.get("exchange")
                    stock_price = stock_info.get("price", 0)  # 주식의 현재 가격을 가져옴
                    stock_value = stock_price * quantity  # 주식의 총 가치를 계산
                    total_stock_value += stock_value  # 총 자산에 더하기
                    stock_message += f"{exchange}:{stock_key}가 {quantity}개, 현재 {stock_price}원, 자산 가치: {stock_value}원\n"
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
                with open(gamble_config_path, "r", encoding="utf-8") as gamble_config_file:
                    gamble_config = json.load(gamble_config_file)

                gamble_config["probability"] = value

                with open(gamble_config_path, "w", encoding="utf-8") as gamble_config_file:
                    json.dump(gamble_config, gamble_config_file, ensure_ascii=False, indent=4)

                await message.channel.send(f"도박의 성공 확률이 {value}%로 설정되었습니다.")

            elif setting_type == "reward":
                # 보상 배율 설정
                with open(gamble_reward_path, "r", encoding="utf-8") as gmable_reward_file:
                    gamble_reward = json.load(gmable_reward_file)

                gamble_reward["multiplier"] = value

                with open(gamble_reward_path, "w", encoding="utf-8") as gamble_reward_file:
                    json.dump(gamble_reward, gamble_reward_file, ensure_ascii=False, indent=4)

                await message.channel.send(f"도박의 보상 배율이 {value}로 설정되었습니다.")

        if message.content == "!로또체크":
            lotto_path = os.path.join(FOLDER, "lotto.json")
            stock_path = os.path.join(FOLDER, "stock.json")

            try:
                # lotto.json 파일 읽기
                with open(lotto_path, "r", encoding="utf-8") as lotto:
                    lotto_data = json.load(lotto)

                # 현금 추출
                total_value = lotto_data["cash"]

                # 주식 가격 계산
                with open(stock_path, "r", encoding="utf-8") as stock:
                    stock_data = json.load(stock)

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
            price_fix("KDJ", "000020", 523)

            stock_path = os.path.join(FOLDER, "stock.json")

            try:
                # stock.json 파일 읽기
                with open(stock_path, "r", encoding="utf-8") as stock:
                    stock_data = json.load(stock)

                if not stock_data:
                    await message.channel.send("등록된 주식이 없습니다.")
                    return

                # 임베드 메시지 생성
                embed = discord.Embed(title="주식 목록", description="등록된 주식들의 정보를 아래에서 확인하세요.", color=discord.Color.blue())

                for stock_key, stock_info in stock_data.items():
                    stock_name = stock_info.get("name", "이름 없음")  # 주식명
                    stock_price = stock_info.get("price", 0)  # 주식 가격
                    stock_nation = stock_info.get("nation", "소속 없음")
                    stock_exchange = stock_info.get("exchange", "거래소 없음")  # 거래소

                    # 각 주식 정보를 임베드에 추가
                    embed.add_field(
                        name=f"<:addon:1308403349829320754> {stock_name} ({stock_nation}의 {stock_exchange}:{stock_key})",
                        value=f"현재 가격: {stock_price}원",
                        inline=True
                    )

                await message.channel.send(embed=embed)

            except Exception as e:
                await message.channel.send(f"주식 목록 조회 중 오류가 발생했습니다: {e}")

        if message.content == "!랭킹":
            stock_random()

            import operator

            account_path = os.path.join(FOLDER, "account.json")
            stock_path = os.path.join(FOLDER, "stock.json")

            try:
                # account.json 읽기
                with open(account_path, "r", encoding="utf-8") as account:
                    account_data = json.load(account)

                # stock.json 읽기
                with open(stock_path, "r", encoding="utf-8") as stock:
                    stock_data = json.load(stock)

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

            embed = discord.Embed(title="사용 가능한 명령어 목록", color=0x3498db)

            # 명령어 설명 추가
            embed.add_field(name="$cmd", value="명령어와 설명을 볼 수 있습니다.", inline=False)
            embed.add_field(name="$nmd <개수>", value="<개수>만큼 메시지를 삭제할 수 있습니다.", inline=True)
            embed.add_field(name="!계좌개설", value="계좌를 생성하고 초기 자금을 설정합니다.", inline=False)
            embed.add_field(name="!이체 <플레이어id> <금액>", value="다른 플레이어에게 금액을 송금합니다.", inline=True)
            embed.add_field(name="!일급", value=f"하루에 한 번 {reward}원을 지급받습니다.", inline=True)
            embed.add_field(name="!주식목록", value="현재 상장된 모든 주식의 정보를 확인합니다.", inline=False)
            embed.add_field(name="!매수 <거래소> <주식코드> <수량>", value="원하는 주식을 지정한 수량만큼 구매합니다.", inline=True)
            embed.add_field(name="!매도 <거래소> <주식코드> <수량>", value="보유 중인 주식을 지정한 수량만큼 판매합니다.", inline=True)
            embed.add_field(name="!주식정보 <거래소> <주식코드>", value="특정 주식의 정보를 확인합니다.", inline=True)
            embed.add_field(name="!지갑", value="현재 자신의 계좌 잔고를 확인합니다.", inline=True)
            embed.add_field(name="!주식기록 <거래소> <주식코드>", value="특정 주식의 가격 변동 기록을 확인합니다.", inline=True)
            embed.add_field(name="!bet <금액>", value="도박을 할 수 있습니다. 금액을 설정하고 도박에 참여하세요.", inline=True)
            embed.add_field(name="!로또참여", value="10만원을 내고 로또에 참가할 수 있습니다. 당신의 운을 시험해보세요.", inline=True)
            embed.add_field(name="!랭킹", value="총 자산의 순위을 볼 수 있습니다. 유저들의 자산을 확인해보세요.", inline=True)
            embed.add_field(name="!세율", value="세율을 볼 수 있습니다. 현행 세율을 확인해보세요.", inline=True)
            embed.add_field(name="!주식그래프 <거래소> <주식코드>", value="주가의 변화를 그래프로 볼 수 있습니다. 주가의 변동을 확인하여 투자 해보세요.", inline=True)
            embed.add_field(name=f"!기부 <금액>", value="기부할 수 있습니다. 기부금은 교육, 의료, 식량, 의류, 주거, 봉사자나 재능기부자의 \n활동비나 실비 지원, 환경, 사회복지, 문화예술, 지방지역사회 활성화 등을 위해 사용됩니다.", inline=True)
            embed.add_field(name="!일당정기소득보기", value="나의 일급을 볼 수 있습니다. 소득에 맞춰 소비수준을 계획해보세요.", inline=True)
            embed.add_field(name="!운세", value="운세를 볼 수 있습니다.", inline=False)
            embed.add_field(name="!궁합 <유저1> <유저2>", value="궁합을 볼 수 있습니다. 유저 간의 궁합을 시험해보세요.", inline=True)
            # embed.add_field(name="!내채팅정보", value="내가 친 채팅의 개수와 나의 레벨을 볼 수 있습니다..", inline=False)
            # embed.add_field(name="!채팅랭킹", value="모두의 채팅정보를 한 번에 봅니다. 채팅을 많이 친 순위로 정리됩니다.", inline=True)

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
            int_changer()
            price_fix("NEX", "000000", 0)
            price_fix("NEX", "000001", 0)
            price_fix("NEX", "000002", 0)
            price_fix("NEX", "000003", 0)
            price_fix("NEX", "000004", 0)
            price_fix("NEX", "000005", 0)
            price_fix("NEX", "000006", 0)
            price_fix("NEX", "000007", 0)
            price_fix("DASDAQ", "000008", 0)
            price_fix("DEX", "000009", 0)
            price_fix("NEX", "000010", 0)
            price_fix("SLEC", "000011", 0)
            price_fix("CCEX", "000012", 0)
            price_fix("CCEX", "000013", 0)
            price_fix("CCEX", "000014", 0)
            price_fix("NEX", "000015", 0)
            price_fix("NEX", "000016", 0)
            price_fix("NEX", "000017", 0)
            price_fix("CCEX", "000018", 0)
            price_fix("NEX", "000019", 0)
            price_fix("KDJ", "000020", 0)
            price_fix("BIGMAC", "000021", 0)
            args = message.content.split()

            if message.attachments:
                if not os.path.exists(folder):
                    os.makedirs(folder)

                file_names = []
                for attachment in message.attachments:
                    file_path = os.path.join(folder, attachment.filename)
                    await attachment.save(file_path)
                    file_names.append(attachment.filename)

                for attachment in message.attachments:
                    await save_image(attachment)
            else:
                if args[0] == "!":
                    await message.channel.purge(limit=1)
                    message_time = message.created_at
                    chatlog = open('chat_log.txt', 'a')
                    chatlog.write(f"[{message_time}] CHAT : 비밀메시지 도착함.\n")
                    chatlog.close()
                    print("비밀 채팅이 도착했습니다")
                else:
                    # DM인지 확인
                    if isinstance(message.channel, discord.DMChannel):  # DM 채널에서 메시지가 왔는지 확인
                        message_time = message.created_at
                        chatlog = open('chat_log.txt', 'a')
                        chatlog.write(f"{message_time} 에 DM에서 {message.author.name} ( {message.author.mention} ) 가 " + "'" + message.content + "'" + " 라고 말함. \n")
                        chatlog.close()
                    else:
                        message_time = message.created_at
                        chatlog = open('chat_log.txt', 'a')
                        chatlog.write(f"{message_time} 에 {message.guild.name} 에서 {message.author.name} ( {message.author.nick} ) ( {message.author.mention} ) 가 {message.channel.mention} 에서 " + "'"+message.content+"'" + " 라고 말함. \n")
                        chatlog.close()

        if message.content.startswith('$nmd'):
            try:
                count = int(message.content.split()[1])
                clear_count = count + 1
                await message.channel.purge(limit=clear_count)
                await message.channel.send(f"{count}개의 메시지가 삭제되었습니다.", delete_after=5)
            except (IndexError, ValueError):
                await message.channel.send("사용법: $nmd [숫자]", delete_after=5)
            except discord.Forbidden:
                await message.channel.send("메시지를 삭제할 권한이 없습니다.", delete_after=5)

    @staticmethod
    async def on_reaction_add(reaction, user):
        stock_random()
        
        if user.bot:
            return

        message_content = reaction.message.content
        reaction_emoji = reaction.emoji
        channel = reaction.message.channel
        message_time = reaction.message.created_at
        message_guild = reaction.message.guild

        nowtime = datetime.now()
        reaction_time = f"{str(nowtime.year)}년 {str(nowtime.month)}월 {str(nowtime.day)}일 {str(nowtime.hour)}시 {str(nowtime.minute)}분 {str(nowtime.second)}초"

        chatlog = open('chat_log.txt', 'a')
        chatlog.write(f"{reaction_time} 에 {user.name}이(가) {message_guild} 서버의 {message_time} 에 작성된 {channel} 에 있는 '{message_content}' 메시지에 {reaction_emoji} 이모지로 반응.\n")
        chatlog.close()

    @staticmethod
    async def on_message_edit(before, after):
        stock_random()
        
        bc = before.content
        ac = after.content
        nowchat = datetime.now()
        edittime = f"{str(nowchat.year)}년 {str(nowchat.month)}월 {str(nowchat.day)}일 {str(nowchat.hour)}시 {str(nowchat.minute)}분 {str(nowchat.second)}초"

        chatlog = open('chat_log.txt', 'a')
        chatlog.write(f"{edittime} 에 {after.guild.name} 서버의 {after.channel} 에서 {after.author} 가 {before.author} 에 의해 {before.created_at} 에 작성된 ' {bc} ' 를 ' {ac} ' 로 수정 \n")
        chatlog.close()

intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
client.run('MTMwNDgwNzE0MTYyMTYzMzAzNA.GJtWRM.Hdz_3S8j0BCI_ypnmsv-rOO9zcAKHf5GNi2fy0')