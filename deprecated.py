# async def send_horoscope(id):
#     today = datetime.datetime.now().strftime("%d.%m.%Y года")
#     await bot.send_message(id, f"ГОРОСКОП НА {today}")
#     horoscopes = get_horoscope()
#     for horoscope in horoscopes.items():
#         await bot.send_photo(
#             id,
#             types.InputFile(horoscope[1][1]),
#             caption=f"{horoscope[0]}\n\n{horoscope[1][0]}",
#             parse_mode="HTML",
#         )


# async def send_forecast(id, day):
#     if day == "today":
#         date = datetime.datetime.now().strftime("%d.%m.%Y года")
#         forecasts = get_weather()["today"]
#     elif day == "tomorrow":
#         date = (datetime.datetime.now() + datetime.timedelta(1)).strftime(
#             "%d.%m.%Y года"
#         )
#         forecasts = get_weather()["tomorrow"]
#     message = f"ПРОГНОЗ ПОГОДЫ на {date}\n\n"
#     for forecast in forecasts.items():
#         message += forecast[0] + "\n"
#     photo = types.InputFile(Counter(forecasts.values()).most_common(1)[0][0])
#     await bot.send_photo(id, photo, caption=message)


# async def send_holidays(id):
#     today = datetime.datetime.now().strftime("%d.%m.%Y года")
#     holidays = get_holidays()
#     message = f"ПРАЗДНИКИ {today}\n\n"
#     for holiday in holidays:
#         message += "🎉 " + holiday + "\n"
#     await bot.send_message(id, message)


# def get_weather() -> dict | None:
#     """
#     It gets the weather forecast for today and tomorrow from an API and
#     returns it in a dictionary.
#     :return: A dictionary with two keys: today and tomorrow.
#     """
#     url = os.getenv("WEATHER")
#     forecast_dict = {"today": {}, "tomorrow": {}}
#
#     try:
#         response = httpx.get(
#             url,  # type: ignore
#             params={
#                 "id": 571476,
#                 "lang": "ru",
#                 "units": "metric",
#                 "APPID": os.getenv("WEATHER_API_KEY"),
#             },
#             headers=headers,
#         )
#     except Exception as e:
#         logging.error("Сайт недоступен")
#         logging.error(e)
#         return
#
#     result = response.json()
#     today = int(datetime.datetime.now().strftime("%d"))
#     for i in result["list"]:
#         if int(i["dt_txt"][8:10]) - today == 1:
#             forecast = (
#                 i["dt_txt"][11:]
#                 + "{0:+3.0f} ".format(i["main"]["temp"])
#                 + i["weather"][0]["description"]
#             )
#             if i["weather"][0]["id"] == 803:
#                 forecast_dict["tomorrow"][forecast] = "images/облачно с прояснением.png"
#             elif i["weather"][0]["main"] == "Snow":
#                 forecast_dict["tomorrow"][forecast] = "images/снег.png"
#             elif i["weather"][0]["main"] == "Rain":
#                 forecast_dict["tomorrow"][forecast] = "images/дождь.png"
#             elif i["weather"][0]["main"] == "Clear":
#                 forecast_dict["tomorrow"][forecast] = "images/ясно.png"
#             elif i["weather"][0]["main"] == "Thunderstorm":
#                 forecast_dict["tomorrow"][forecast] = "images/дождь с гроза.png"
#             elif i["weather"][0]["main"] == "Clouds":
#                 forecast_dict["tomorrow"][forecast] = "images/облачно.png"
#         elif int(i["dt_txt"][8:10]) == today:
#             forecast = (
#                 i["dt_txt"][11:]
#                 + "{0:+3.0f} ".format(i["main"]["temp"])
#                 + i["weather"][0]["description"]
#             )
#             if i["weather"][0]["id"] == 803:
#                 forecast_dict["today"][forecast] = "images/облачно с прояснением.png"
#             elif i["weather"][0]["main"] == "Snow":
#                 forecast_dict["today"][forecast] = "images/снег.png"
#             elif i["weather"][0]["main"] == "Rain":
#                 forecast_dict["today"][forecast] = "images/дождь.png"
#             elif i["weather"][0]["main"] == "Clear":
#                 forecast_dict["today"][forecast] = "images/ясно.png"
#             elif i["weather"][0]["main"] == "Thunderstorm":
#                 forecast_dict["today"][forecast] = "images/дождь с гроза.png"
#             elif i["weather"][0]["main"] == "Clouds":
#                 forecast_dict["today"][forecast] = "images/облачно.png"
#     return forecast_dict


# def get_horoscope() -> dict:
#     """
#     It gets the horoscope for each sign from the website and returns a
#     dictionary with the sign name as the key and the horoscope text and
#     image path as the value.
#     :return: A dictionary with the name of the sign as the key and a tuple as
#     the value. The tuple contains the horoscope text and the image path.
#     """
#     horoscope = {}
#     signs = {
#         "aries": ["Овен", "images/овен.png"],
#         "taurus": ["Телец", "images/Телец.png"],
#         "gemini": ["Близнецы", "images/блезнецы.png"],
#         "cancer": ["Рак", "images/рак.png"],
#         "leo": ["Лев", "images/лев.png"],
#         "virgo": ["Дева", "images/дева.png"],
#         "libra": ["Весы", "images/весы.png"],
#         "scorpio": ["Скорпион", "images/скорпион.png"],
#         "sagittarius": ["Стрелец", "images/стрелец.png"],
#         "capricorn": ["Козерог", "images/козерог.png"],
#         "aquarius": ["Водолей", "images/водолей.png"],
#         "pisces": ["Рыбы", "images/рыбы.png"],
#     }
#     for sign in signs.items():
#         try:
#             response = httpx.get(
#                 f"https://horo.mail.ru/prediction/{sign[0]}/today/", headers=headers
#             )
#             result = response.text
#             soup = BeautifulSoup(result, "lxml")
#             horoscope_text = soup.find(
#                 "div",
#                 class_=(
#                     "article__item article__item_alignment_left " "article__item_html"
#                 ),
#             ).text
#             horoscope[sign[1][0]] = horoscope_text, sign[1][1]
#         except Exception as e:
#             horoscope["Exception horoscope"] = e
#     return horoscope


# def get_holidays():
#     """
#     It takes a url, makes a request to that url, parses the response, and
#     returns a list of holidays
#     :return: A list of holidays
#     """
#     url = os.getenv("HOLY")
#     holidays = []
#     try:
#         response = httpx.get(url, headers=headers)
#         result = response.text
#         soup = BeautifulSoup(result, "lxml")
#         holidays_list = soup.find("ul", class_="holidays-items").find_all("li")
#         for holiday in holidays_list:
#             holiday = holiday.text[:-5]
#             holidays.append(holiday)
#         return holidays
#     except Exception as e:
#         logging.error(f"Сайт {url} недоступен")
#         logging.error(e)
#
