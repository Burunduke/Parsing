import bs4
import lxml
from bs4 import BeautifulSoup
import requests
import string
import codecs
import json


def main():
    # Этап 1 - с каждой из 502 страниц считываем все ссылки на статьи -> записываем в текстовый файл
    news_url_list = []

    for i in range(1, 502):
        r = requests.get(url = f"https://www.finanz.ru/novosti/glavnye-novosti?p={i}", headers = headers)
        result = r.content
        soup = BeautifulSoup(result, "lxml")
        links = soup.find_all(class_ = "news_title")
        for link in links:
            news_url = link.get("href")
            if news_url not in news_url_list:
                news_url_list.append(news_url)
    with open("news_url_list.txt", "a",encoding="utf-8") as file:
        for line in news_url_list:
            file.write(f"https://www.finanz.ru{line}\n")

    headers = {
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 OPR/78.0.4093.186"
    }

    # редактируем ссылки
    lines = []
    with open("news_url_list.txt","r",encoding='utf-8') as file:
        for line in file:
            lines.append(line.strip())

    # Создаем библиотеку из url, даты, заголовка и текста всех полученных сверху ссылок
    data_dict = []

    for line in lines:
        try:
            r = requests.get(line,headers=headers)
            result = r.content.decode("utf-8")
            soup = BeautifulSoup(result, "lxml")
            for script in soup(["script", "style"]):
                script.extract()

            date = soup.find(class_ = "main_background").find(class_ = 'title_more').find("h2").find("span").text
            date = date[1:11]

            title = soup.find(class_ = "news_title").text

            text = soup.find(class_ = "news_text").text.strip()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            text.encode('utf-8').decode('utf-8')


            data = {
                "url" : line,
                "date" : date,
                "title" : title,
                "text" : text
            }
            data_dict.append(data)


        except requests.exceptions.TooManyRedirects:
            pass

    # всю библиотеку записываем в json
    with open("data.json", "a", encoding="utf-8") as json_file:  # ,encoding="utf-8"
        json.dump(data_dict, json_file, indent=4, ensure_ascii=False)  # , ensure_ascii=False

if __name__ == "__main__":
    main()