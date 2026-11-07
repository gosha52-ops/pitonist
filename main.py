import os
from pathlib import Path
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup
import requests


def download_image(url, folder_name='images/'):
    os.makedirs(folder_name, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    pathname = urlsplit(url).path
    image_name = os.path.split(pathname)[-1]
    file_path = os.path.join(folder_name, image_name)
    with open(file_path, 'wb') as file:
        file.write(response.content)


def download_book_text(url, book_name, folder_name="books"):
    os.makedirs(folder_name, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    file_name = f"{book_name}.txt"
    file_path = os.path.join(folder_name, file_name)
    with open(file_path, 'w', encoding="utf8") as file:
        file.write(response.text)


def get_book_urls(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    new_books = soup.find('div', class_='b-thumbnails')
    info_new_books = new_books.find_all('div', class_='b-thumbnail')
    book_urls = []
    for book in info_new_books:
        link = book.find('a')['href']
        book_urls.append(link)
    return book_urls


def get_book_info(book_url, url):
    response = requests.get(book_url)
    response.raise_for_status()
    book_soup = BeautifulSoup(response.text, 'lxml')
    image_url = book_soup.find("div", class_="big-book-left-block").find("img")['src']
    base_url = urljoin(url, image_url)
    book_name = book_soup.find("h1").text
    book_info = book_soup.find_all("div", class_="big-book-stat")
    all_books_info = []
    for info in book_info:
        if info.find('a') is None:
            continue
        book_info = info.find('a').text
        all_books_info.append(book_info)
    return base_url, book_name, all_books_info


def get_txt_link(book_url, url):
    response = requests.get(book_url)
    response.raise_for_status()
    book_soup = BeautifulSoup(response.text, 'lxml')
    download_links = book_soup.find_all('div', class_="download-link")
    txt_download_link = None
    for link in download_links:
        download_link = link.find("a")["href"]
        extention = Path(download_link).suffix
        if extention == ".txt":
            txt_download_link = urljoin(url, download_link)
            print(txt_download_link)
            break
    return txt_download_link


def main():
    url = "https://knigofil.org"
    book_urls = get_book_urls(url)
    for book_url in book_urls:
        base_url, book_name, all_books_info = get_book_info(book_url, url)
        print(f""" 
        Название: {book_name} 
        Автор: {all_books_info[0]} 
        Жанр: {all_books_info[1]} 
        Год: {all_books_info[2]}""")
        txt_download_link = get_txt_link(book_url, url)
        if txt_download_link is None:
            print("Ссылка не найдена")
            continue
        download_book_text(txt_download_link, book_name)
        download_image(base_url)


if __name__ == '__main__':
    main()