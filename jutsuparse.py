import aiohttp
import bs4
import re
from dataclasses import dataclass


@dataclass
class JutEpisode():
    url: str
    name: str


@dataclass
class JutAnime():
    name: str
    url: str
    img: str

    async def get_episodes(self):
        async with await create_session() as session:
            async with session.get(self.url) as resp:
                bs = bs4.BeautifulSoup(await resp.text(), 'html.parser')
                for i in bs.select('.video'):
                    url = i.get('href')
                    name = ""
                    async with session.get('http://jut.su' + url) as vresp:
                        vbs = bs4.BeautifulSoup(await vresp.text(), 'html.parser')
                        name = ''.join(vbs.select_one(
                            '.video_plate_title').select_one('h2').contents)
                    yield JutEpisode(url, name)


async def create_session() -> aiohttp.ClientSession:
    s = aiohttp.ClientSession()
    s.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0'
    await s.head('http://jut.su/anime/')
    return s


async def get_animes(name: str):
    async def parse(raw: str) -> list[JutAnime]:
        parse_results: list[JutAnime] = []

        soup = bs4.BeautifulSoup(raw, 'html.parser')
        animes: bs4.ResultSet[bs4.Tag] = soup.find_all(
            'div', class_='all_anime_global')
        for i in animes:
            body = i.select_one('.all_anime')

            url = 'http://jut.su' + str(i.select_one('a').get('href'))
            img = re.search(r"'(https:\/\/.*?)'",
                            body.select_one('.all_anime_image').get('style')).group()
            name = ''.join(body.select_one('.aaname').contents)

            parse_results.append(JutAnime(name, url, img))
        return parse_results

    async with await create_session() as session:
        session.headers['Referer'] = 'http://jut.su/anime/'

        await session.head('http://jut.su/anime/')

        payload = {'ajax_load': 'yes', 'start_from_page': 1,
                   'show_search': name, 'anime_of_user': ''}
        async with session.post('https://jut.su/anime/', data=payload) as resp:
            return await parse(await resp.text())
