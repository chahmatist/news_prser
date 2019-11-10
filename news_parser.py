import requests
from bs4 import BeautifulSoup as Bs
from jinja2 import Environment, FileSystemLoader
import os

TIME_OUT = 10.0
TIME_OUT_read = 1.0


def links_news(response_text):
    soup = Bs(response_text, 'lxml')
    content_posts = soup.find('div', {'class': 'post-list'})
    links = []
    for link in content_posts.findAll('a', {'class': 'entry-title'}):
        links.append(link.get('href'))
    return links


def get_content(links):
    post = []
    for link in links:
        html = get_html(link)
        soup = Bs(html, 'lxml')
        [x.extract() for x in soup.find_all('script')]
        [x.extract() for x in soup.find_all('style')]
        [x.extract() for x in soup.find_all('meta')]
        [x.extract() for x in soup.find_all('noscript')]
        entry_content = soup.find('div', {'class': 'entry-content'})
        title = entry_content.find('h1', {'class': 'entry-title'})
        content = entry_content.find('div', {'class': 'content'})
        if content.find('div', {'class': 'wp-polls'}):
            content.find('div', {'class': 'wp-polls'}).decompose()

        post.append({
            'title': title.text,
            'content': content.text,
        })
    return post


def gen_html(data):
    root = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(root, 'templates')
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template('base.html')

    filename = os.path.join(root, 'html', 'index.html')
    with open(filename, 'w') as fh:
        fh.write(template.render(
            posts=enumerate(data),
        ))


def get_html(url):
    with requests.Session() as r:
        page = None
        while True:
            headers = get_headers()
            try:
                page = r.get(url, headers=headers,
                             timeout=(TIME_OUT, TIME_OUT_read))
            except ConnectionError:
                print('ConnectionError')
                pass
            except requests.exceptions.ReadTimeout:
                print('requests.exceptions.ReadTimeout')
                pass
            else:
                return page.text
                break


def get_headers():
    return {
        "Accept": "text/html,application/xhtml+xml,"
                  "application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Host": "pasmi.ru",
        "Referer": "https://pasmi.ru/tag/opros/",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0)"
                      " Gecko/20100101 Firefox/70.0"
    }


url_links = 'https://pasmi.ru/cat/news/'
links = links_news(get_html(url_links))
data = get_content(links)
gen_html(data)
