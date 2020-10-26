import bs4
import aiohttp
import asyncio
from dataclasses import dataclass, field
from typing import List, Optional
from const import Color
import yaml


@dataclass
class Topic:
    title: str
    url: str
    open: bool = False


@dataclass
class CustomText:
    text: str
    color: Optional[str] = None
    bold: bool = False


class Prodota:
    def __init__(self):
        self.base_url = 'https://prodota.ru/forum'
        self.topics = list()
        self.session = None
        with open('../config.yaml', encoding='utf-8') as file:
            self.config = yaml.load(file, Loader=yaml.FullLoader)['prodota']

    async def get_topics(self, forum_id: int = 45) -> List[Topic]:
        topics = list()

        async with self.session.get(f'{self.base_url}/{forum_id}') as response:
            html = await response.text()
            soup = bs4.BeautifulSoup(html, features='html.parser')
            for h4 in soup.find_all('h4', class_='ipsDataItem_title'):
                a = h4.find('a')
                lock = True if h4.find('i', class_='fa-lock') else False
                if a and 'title' in a.attrs:
                    topics.append(Topic(title=a['title'], url=a['href'].split('/?')[0], open=not lock))

        return topics

    async def update_topics(self):
        self.topics = await self.get_topics()

    @staticmethod
    def compose_text(colored_texts: List[List[CustomText]]) -> str:
        composed_text = ''

        for line in colored_texts:
            composed_text += '<p>'

            for colored_text in line:
                _text = colored_text.text

                if colored_text.color:
                    _text = f'<span style="color:{colored_text.color};">{_text}</span>'

                if colored_text.bold:
                    _text = f'<b>{_text}</b>'

                if colored_text != line[-1]:
                    _text += ' '

                composed_text += _text

            composed_text += '</p>'
            composed_text += '\n'

        return composed_text

    async def post(self, topic_url: str, text: str, color: str = None):
        # TODO перенести в отдельную функцию получение этой продота хуйни
        async with self.session.get(topic_url) as response:
            html = await response.text()
            soup = bs4.BeautifulSoup(html, features='html.parser')

            last_page = soup.find('li', {'class': 'ipsPagination_last'}).find('a')['data-page']

        async with self.session.get(f'{topic_url}/page/{last_page}') as response:
            # TODO HANDLE EXCEPTIONS
            html = await response.text()
            soup = bs4.BeautifulSoup(html, features='html.parser')
            csrf_key = soup.find('input', {'name': 'csrfKey'})['value']
            plupload = soup.find('input', {'name': 'plupload'})['value']
            max_file_size = soup.find('input', {'name': 'MAX_FILE_SIZE'})['value']

            last_comment_url = [a['href'] for a in soup.find_all('a') if 'href' in a.attrs and 'comment=' in a['href']][-1]
            last_seen_id = int(last_comment_url.split('=')[-1])

        data = {
            'commentform_217907_submitted': 1,
            'csrfKey': csrf_key,
            '_contentReply': 1,
            'MAX_FILE_SIZE': max_file_size,
            'plupload': plupload,
            'topic_comment_217907': f'<p><span style="color:{Color.blue};">{text}</span></p>',
            'topic_comment_217907_upload': 'c89199d4252c000ec70d261ea505574c',
            'topic_auto_follow': 0,
            'currentPage': last_page,
            '_lastSeenID': last_seen_id
        }

        async with self.session.post(f'https://prodota.ru/forum/topic/217907/page/770/', data=data) as response:
            # TODO LOGGING
            print(f'post result {response.status}')

    async def get_latest_page(self, topic_id: int):
        pass

    async def private_message(self, text: str, title: str, targets: List[str]):
        async with self.session.get(f'{self.base_url}/messenger/') as response:
            html = await response.text()
            soup = bs4.BeautifulSoup(html, features='html.parser')

            for a in soup.find_all('a'):
                if 'href' in a.attrs and 'csrfKey=' in a['href'] and '&' not in a['href']:
                    csrf_key_compose = a['href'].split('csrfKey=')[-1]
                    print(csrf_key_compose)
                    break

        async with self.session.get(f'{self.base_url}/messenger/compose/?csrfKey={csrf_key_compose}') as response:
            # TODO HANDLE EXCEPTIONS
            html = await response.text()
            soup = bs4.BeautifulSoup(html, features='html.parser')
            csrf_key = soup.find('input', {'name': 'csrfKey'})['value']
            plupload = soup.find('input', {'name': 'plupload'})['value']
            max_file_size = soup.find('input', {'name': 'MAX_FILE_SIZE'})['value']

        data = {
            'form_submitted': 1,
            'csrfKey': csrf_key,
            'MAX_FILE_SIZE': max_file_size,
            'plupload': plupload,
            'messenger_to_original': '',
            'messenger_to': '\n'.join(targets),
            'messenger_title': title,
            'messenger_content': text,
            'messenger_content_upload': '67b121390ac1f5f3eb484a60092c9640'
        }

        print(data)

        async with self.session.post(f'{self.base_url}/messenger/compose/', data=data) as response:
            print('PRIVATE MESSAGE COMPOSED' + response.status)

    async def authorize(self, login: str = None, password: str = None):
        if not login:
            login = self.config['user']

        if not password:
            password = self.config['password']

        self.session = aiohttp.ClientSession()

        async with self.session.get(self.base_url) as response:
            html = await response.text()
            soup = bs4.BeautifulSoup(html, features='html.parser')
            csrf_key = soup.find('input', {'name': 'csrfKey'})['value']
            ref = soup.find('input', {'name': 'ref'})['value']

        post_data = {
            'csrfKey': csrf_key,
            'ref': ref,
            'auth': login,
            'password': password,
            'remember_me': 1,
            '_processLogin': 'usernamepassword'}

        async with self.session.post(f'{self.base_url}/login/', data=post_data) as response:
            if response.status == 200:
                # TODO LOGGING
                print('authorized')

