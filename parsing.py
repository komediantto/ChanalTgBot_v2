from collections.abc import Generator
import re
import traceback
from typing import Union
import httpx
import redis
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import datetime
import logging
from selenium import webdriver
from mytypes import Post
from settings import config


logging.basicConfig(
    filename=f"{__name__}.log", level=logging.INFO, filemode="w", encoding="UTF-8"
)


ua = UserAgent()

headers = {"user-agent": str(ua.chrome)}

redis = redis.Redis(config.REDIS_HOST, 6379, 0)


hashtags = "#ПервыйГородской #Брянск #БрянскаяОбласть #Новости #НовостиБрянска  #ЧП #news #32регион #bryansk #происшествия #срочныеновости"
hashtags_ria = "#москва #москвасити #московскаяобласть #новости #новостимосквы #россия #москвасегодня #ЧП #news #moscow #moscowcity #moscowmule #moscowdays #происшествия #срочныеновости"


def convert_vk_video_link(input_link):
    match = re.search(r"oid=-(\d+)&id=(\d+)", input_link)
    if match:
        oid = match.group(1)
        video_id = match.group(2)

        new_link = f"https://vk.com/video-{oid}_{video_id}"
        return new_link
    else:
        return None


def get_urgent_information() -> dict | None:
    """
    It gets the latest news from the website of the Ministry of Emergency
    Situations of Russia
    :return: A dictionary with the title of the news
    as the key and the link to the
    news as the value.
    """
    url = config.MCHS
    urgent_news = {}
    try:
        response = httpx.get(url, headers=headers)  # type: ignore
    except Exception as e:
        logging.error("Нет ответа от сервера")
        logging.error(e)
        return
    result = response.text
    soup = BeautifulSoup(result, "lxml")
    today = int(datetime.datetime.now().strftime("%d"))
    articles_list = soup.find_all("div", class_="articles-item")
    for article in articles_list:
        article_date = article.find("span", class_="articles-item__date").text
        if today - int(article_date[:2]) <= 1:
            article_title = article.find("a", class_="articles-item__title").text
            article_href = "https://32.mchs.gov.ru" + article.find(
                "a", class_="articles-item__title"
            ).get("href")
            urgent_news[article_title] = article_href
    return urgent_news


def get_urgent_information_polling() -> str | None:
    """
    It gets the latest news from the site, checks if it's already in the
    database, if not, it adds it to the database and returns the message.
    :return: a message.
    """
    url = config.MCHS
    try:
        response = httpx.get(url, headers=headers)  # type: ignore
        result = response.text
        soup = BeautifulSoup(result, "lxml")
        title = soup.find("a", class_="articles-item__title").text  # type: ignore
        article_href = (
            soup.find("div", class_="articles-item")
            .find("a", class_="articles-item__title")  # type: ignore
            .get("href")  # type: ignore
        )
        response = httpx.get(f"https://32.mchs.gov.ru{article_href}", headers=headers)

    except Exception as e:
        logging.error(f"Сайт {url} недоступен")
        logging.error(e)
        return

    result = response.text
    soup = BeautifulSoup(result, "lxml")
    text = soup.find("div", itemprop="articleBody").find_all("p", limit=15)  # type: ignore
    message = f"{title}\n\n"
    for p in text:
        message += p.text
    image: str = soup.find("div", class_="public").find("img").get("src")  # type: ignore
    image_url = "https://32.mchs.gov.ru" + image
    if redis.get(message) is not None:
        if redis.get(message) != image_url.encode():
            redis.set(message, image_url)
            return message
        else:
            return None
    else:
        logging.info(f"Ключа {message[:10]} не существует.")
        redis.set(message, image_url)
        return message


def get_info_from_newbryansk() -> Generator[Union[Post, None], None, None]:
    """
    It gets the latest news from the site, checks if the image is in the redis
    database, if not, it adds it to the database and returns the image and the
    text of the news.
    :return: a tuple of two elements.
    """
    urls = config.NEWBR.split(",")
    for url in urls:
        try:
            response = httpx.get(url, headers=headers, timeout=15.0)
            result = response.text
            soup = BeautifulSoup(result, "lxml")
            new_href: str = (
                soup.find("div", class_="content-container")
                .find("div", class_="main-news-list")  # type:ignore
                .find(  # type:ignore
                    "div", class_="big-news-list-block extreme-news-list"  # type:ignore
                )
                .find("h2")  # type:ignore
                .find("a")  # type:ignore
                .get("href")  # type:ignore
            )
            new_href_url = "https://newsbryansk.ru/" + new_href
            response = httpx.get(new_href_url, headers=headers)

        except Exception:
            logging.error(f"Сайт {url} недоступен")
            logging.error(traceback.format_exc())
            continue

        result = response.text
        soup = BeautifulSoup(result, "lxml")
        title = (
            soup.find("div", class_="detale-news-block__pin")
            .find("h1")  # type:ignore
            .text  # type:ignore
        )
        text = soup.find("span", itemprop="articleBody").find_all(  # type:ignore
            "p", limit=6
        )
        image: str = (
            soup.find("div", class_="detale-news-block__image")
            .find("img")  # type:ignore
            .get("src")  # type:ignore
        )
        message = f"{title}\n\n"
        for p in text:
            message += p.text
        message += f"\n{hashtags}\n\nИсточник: {url}"
        post = Post(image, "photo", message)
        if redis.get(post.url) is not None:
            if post.url.encode() not in redis.keys():
                redis.set(post.url, post.text, datetime.timedelta(days=2))
                yield post
            else:
                yield None
        else:
            logging.info("Новый пост!")
            redis.set(post.url, post.text, datetime.timedelta(days=2))
            yield post


def get_info_from_ria() -> Post | None:
    """
    It gets the latest news from the site, parses it, and returns the image and
    text of the news
    :return: a tuple of two elements: image and message.
    """
    url = config.RIA
    try:
        response = httpx.get(url, headers=headers)
        result = response.text
        soup = BeautifulSoup(result, "lxml")
        new_href: str = (
            soup.find("div", class_="list list-tags")
            .find("div", class_="list-item")  # type:ignore
            .find("div", class_="list-item__content")  # type:ignore
            .find(  # type:ignore
                "a", class_=("list-item__title " "color-font-hover-only")  # type:ignore
            )
            .get("href")  # type:ignore
        )
        response = httpx.get(new_href, headers=headers)
    except Exception:
        logging.error(f"Сайт {url} недоступен")
        logging.error(traceback.format_exc())
        return

    result = response.text
    soup = BeautifulSoup(result, "lxml")
    video_tags = soup.find("meta", property="og:video")
    if video_tags:
        image: tuple[str, str] = (video_tags.get("content"), "video")  # type:ignore
    else:
        image: tuple[str, str] = (
            soup.find("div", class_="media").find("img").get("src"),
            "photo",
        )  # type:ignore
    title = soup.find("div", class_="article__title").text  # type:ignore
    text = soup.find_all("div", class_="article__block", limit=2)
    message = f"{title}\n\n"
    for p in text:
        abzac = p.text
        message += abzac + "\n\n"
    message += f"{hashtags_ria}\n\nИсточник: {url}"
    post = (
        Post(image[0], "photo", message)
        if image[1] == "photo"
        else Post(image[0], "video", message)
    )
    if redis.get(post.url) is not None:  # type:ignore
        if post.url.encode() not in redis.keys():  # type:ignore
            redis.set(post.url, post.text, datetime.timedelta(days=2))  # type:ignore
            return post
        else:
            return None
    else:
        logging.info("Новый пост!")
        redis.set(post.url, post.text, datetime.timedelta(days=2))  # type:ignore
        return post


def get_info_from_bga() -> Post | None:
    """
    It gets the latest news from the site, parses it, and returns the image and
    text of the news
    :return: a tuple of two elements: image and message.
    """
    url = config.BGA
    try:
        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
        driver.get(url)

        driver.execute_script("location.reload();")

        response = driver.page_source
        soup = BeautifulSoup(response, "lxml")
        new_title = (
            soup.find("div", class_="c9")
            .find("div", class_="oneNewsBlock")  # type:ignore
            .find("a")  # type:ignore
            .get("title")  # type:ignore
        )
        new_href: str = (
            soup.find("div", class_="c9")
            .find("div", class_="oneNewsBlock")  # type:ignore
            .find("a")  # type:ignore
            .get("href")  # type:ignore
        )
        driver.get(new_href)
        driver.execute_script("location.reload();")
        response = driver.page_source
        driver.close()
    except Exception:
        logging.error(f"Сайт {url} недоступен")
        logging.error(traceback.format_exc())
        return

    soup = BeautifulSoup(response, "lxml")
    message = f"{new_title}\n\n"
    video_tags = soup.find_all("iframe")
    text = soup.find("div", class_="c9").find_all(["h2", "p"], limit=5)  # type:ignore
    if video_tags:
        image: tuple[str, str] = (video_tags[0].get("src"), "video")
    else:
        image: tuple[str, str] = (
            soup.find("div", class_="c9").find("img").get("src"),
            "photo",
        )  # type:ignore
    for p in text:
        message += p.text
    message += f"\n\n{hashtags}\n\nИсточник: {url}"
    post = (
        Post(image[0], "photo", message)
        if image[1] == "photo"
        else Post(image[0], "video", message)
    )
    if redis.get(post.url) is not None:  # type:ignore
        if post.url.encode() not in redis.keys():  # type:ignore
            redis.set(post.url, post.text, datetime.timedelta(days=2))  # type:ignore
            return post
        else:
            return None
    else:
        logging.info("Новый пост!")
        redis.set(post.url, post.text, datetime.timedelta(days=2))  # type:ignore
        return post


def get_info_from_bryanskobl() -> Post | None:
    """
    It gets the latest news from the site, parses it, and returns the image and
    text of the news
    :return: a tuple of two values.
    """
    url = config.BO
    try:
        response = httpx.get(url, headers=headers)

        result = response.text

        soup = BeautifulSoup(result, "lxml")
        new_title = (
            soup.find("div", class_="grid_12")
            .find("div", class_="grid_10 omega")  # type:ignore
            .find("div", class_="news-header-item")  # type:ignore
            .find("a")  # type:ignore
            .text  # type:ignore
        )
        new_href: str = (
            soup.find("div", class_="grid_12")
            .find("div", class_="grid_10 omega")  # type:ignore
            .find("div", class_="news-header-item")  # type:ignore
            .find("a")  # type:ignore
            .get("href")  # type:ignore
        )
        new_href_url = "http://www.bryanskobl.ru" + new_href
        response = httpx.get(new_href_url, headers=headers)
    except Exception as e:
        logging.error(f"Сайт {url} недоступен")
        logging.error(e)
        return

    result = response.text
    soup = BeautifulSoup(result, "lxml")
    text = (
        soup.find("div", class_="grid_12")  # type:ignore
        .find("div", class_="news-content")  # type:ignore
        .find_all("p", limit=3)  # type:ignore
    )
    try:
        image = "http://www.bryanskobl.ru" + soup.find(  # type:ignore
            "div", class_="grid_12"
        ).find(  # type:ignore
            "div", class_="grid_8 alpha photo-container"  # type:ignore
        ).find(  # type:ignore
            "img", class_="image-border"  # type:ignore
        ).get(  # type:ignore
            "src"
        )
    except Exception:
        image = None
    message = f"{new_title}\n\n"
    for p in text:
        message += p.text + "\n"
    message += f"{hashtags}\n\nИсточник: {url}"
    post = Post(image, "photo", message)
    if redis.get(new_href_url) is not None:
        if new_href_url.encode() not in redis.keys():
            redis.set(new_href_url, message, datetime.timedelta(days=2))
            return post
        else:
            return None
    else:
        logging.info("Новый пост!")
        redis.set(new_href_url, message, datetime.timedelta(days=2))
        return post


def get_info_from_gub() -> Generator[Union[Post, None], None, None]:
    urls = config.GUB_ACS.split(",")
    for url in urls:
        try:
            response = httpx.get(url, headers=headers)
            result = response.text
            soup = BeautifulSoup(result, "lxml")
            article: str = (
                soup.find("div", class_="article").find("a").get("href")  # type:ignore
            )
            response = httpx.get(article, headers=headers)
        except Exception as e:
            logging.error(f"Сайт {url} недоступен")
            logging.error(e)
            continue

        result = response.text
        soup = BeautifulSoup(result, "lxml")
        title = soup.find("div", class_="single_post").find("h1").text  # type:ignore
        video_tags = soup.find_all("iframe")
        if video_tags:
            image = (video_tags[0].get("src"), "video")
            if "vk" in image[0]:
                image = (convert_vk_video_link(image), "video")
        else:
            image = (soup.find("div", class_="thecontent").find("img").get("src"), "photo")  # type: ignore
        text = soup.find("div", class_="thecontent").find_all(  # type:ignore
            "p", limit=2
        )
        message = f"{title}\n\n"
        for p in text:
            message += p.text + "\n\n"
        message += f"{hashtags}\n\nИсточник: {url}"
        post = Post(image[0], "photo", message) if image[1] == "photo" else Post(image[0], "video", message)  # type: ignore
        if redis.get(article) is not None:
            if article.encode() not in redis.keys():
                redis.set(article, message, datetime.timedelta(days=2))
                yield post
            else:
                return None
        else:
            logging.info("Новый пост!")
            redis.set(article, message, datetime.timedelta(days=2))
            yield post


def get_info_from_brgaz() -> Post | None:
    url = config.BRGAZ
    try:
        response = httpx.get(url, headers=headers, timeout=60)
        result = response.text
        soup = BeautifulSoup(result, "lxml")
        article: str = (
            soup.find("div", class_="col-lg-12 top-cat-news")
            .find("a")  # type: ignore
            .get("href")  # type:ignore
        )
        response = httpx.get(article, headers=headers)
    except Exception:
        logging.error(f"Сайт {url} недоступен")
        logging.error(traceback.format_exc())
        return

    result = response.text
    soup = BeautifulSoup(result, "lxml")
    title = soup.find("h1").text  # type:ignore
    image = (
        soup.find("article")
        .find("img", class_="single-top-img")  # type:ignore
        .get("src")  # type:ignore
    )
    text = soup.find("div", class_="video-show").find_all("p", limit=2)  # type:ignore
    message = f"{title}\n\n"
    for p in text:
        message += p.text + "\n\n"
    message += f"{hashtags}\n\nИсточник: {url}"
    post = Post(image, "photo", message)  # type: ignore
    if redis.get(post.url) is not None:  # type:ignore
        if post.url.encode() not in redis.keys():  # type:ignore
            redis.set(post.url, post.text, datetime.timedelta(days=2))  # type:ignore
            return post
        else:
            return None
    else:
        logging.info("Новый пост!")
        redis.set(image, message, datetime.timedelta(days=2))  # type:ignore
        return post


def get_info_from_bn() -> Post | None:
    url = config.BN
    try:
        response = httpx.get(url, headers=headers)
        result = response.text
        soup = BeautifulSoup(result, "lxml")
        article: str = (
            soup.find("div", class_="loop")
            .find("article")  # type:ignore
            .find("a")  # type:ignore
            .get("href")  # type:ignore
        )
        response = httpx.get(article, headers=headers)
    except Exception:
        logging.error(f"Сайт {url} недоступен")
        logging.error(traceback.format_exc())
        return
    result = response.text
    soup = BeautifulSoup(result, "lxml")
    title = soup.find("h1").text  # type:ignore
    image = soup.find("div", class_="loop").find("img").get("src")  # type:ignore
    text = soup.find("div", class_="entry-content").find_all("p", limit=2)  # type: ignore
    message = f"{title}\n\n"
    for p in text:
        message += p.text + "\n\n"
    post = Post(image, "photo", message)
    if redis.get(post.url) is not None:  # type:ignore
        if post.url.encode() not in redis.keys():  # type:ignore
            redis.set(post.url, post.text, datetime.timedelta(days=2))  # type:ignore
            return post
        else:
            return None
    else:
        logging.info("Новый пост!")
        redis.set(image, message, datetime.timedelta(days=2))  # type: ignore
        return post
