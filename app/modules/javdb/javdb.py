import requests
import re
import os
import time
import random
import logging
import requests
import requests_cache
import unicodedata
from lxml.html import fromstring
from requests.adapters import HTTPAdapter
from pydantic import BaseModel
from typing import Optional, Union, Tuple, List, Any, Dict
from bs4 import BeautifulSoup
from anti_useragent import UserAgent

# try:
#     from utils.http import RequestUtils
#     from schemas.javdb import JavActor
# except:
#     pass


logger = logging.getLogger(__name__)


class TimeoutHTTPAdapter(HTTPAdapter):

    DEFAULT_TIMEOUT = 10 # seconds

    def __init__(self, *args, **kwargs):
        self.timeout = TimeoutHTTPAdapter.DEFAULT_TIMEOUT
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)
    

class Movie(BaseModel):
    movie_id: str
    movie_title: str=""
    movie_date: str=""
    movie_series: str=""
    movie_score: str=""
    movie_type: str=""
    movie_actors: str=""
    movie_cover: str=""
    movie_href:str=""
    exist_in_emby:str=""
    
class Link(BaseModel):
    movie_id: str
    link: str=""
    link_name: str=""
    link_meta: str=""
    link_tags: str=""
    link_date: str=""

class JavActor(BaseModel):
    # javdb上的id
    id: str
    # javdb上的演员名
    name: str
    # javdb上的所有曾用演员名
    names: Union[str, list]
    # 自定义名称
    custom_name: Optional[str] = ""
    # 头像链接
    avatar: Optional[str] = ""
    # 演员类型
    type: Optional[str] = ""

# class JavDB:
#     def __init__(self,
#                  base_url: str,
#                  proxy: Union[str, dict] = None,
#                  cookies: Union[str, dict] = None):

#         # javdb的域名
#         self.base_url = base_url.rstrip("/")
#         # 请求javdb的消息头
#         headers = {
#             "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
#             "Accept-Language": "zh-CN,zh;q=0.9",
#             "Upgrade-Insecure-Requests": "1",
#             "Priority": "u=0, i",
#             "Sec-Ch-Ua": '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
#             "Sec-Ch-Ua-Mobile": "?0",
#             "Sec-Ch-Ua-Platform":"Windows",
#             "Sec-Fetch-Dest": "document",
#             "Sec-Fetch-Mode": "navigate",
#             "Sec-Fetch-Site": "same-origin",
#             "Sec-Fetch-User": "?1",
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0"
#         }

#         # 判断是否需要proxy
#         if isinstance(proxy, str):
#             proxies = {
#                 "http": proxy.rstrip("/"),
#                 "https": proxy.rstrip("/")
#             }
#         elif isinstance(proxy, dict) or (proxy is None) :
#             proxies = proxy

#         # 初始化请求request
#         self.request = RequestUtils(headers=headers, cookies=cookies, proxies=proxies, timeout=10)

#     def get_actors_by_type(self, actor_type: str, page: int) -> list[JavActor]:
#         """根据分类获取演员信息

#         Args:
#             actor_type (str): 演员类型, censored/uncensored/western

#         Returns:
#             list[JavActor]: 演员信息
#         """
#         actors: list[JavActor] = []

#         if page == 1:
#             endpoint = f"{self.base_url}/actors/{actor_type}"
#         else:
#             time.sleep(random.uniform(0,1))
#             endpoint = f"{self.base_url}/actors/{actor_type}?page={page}"

#         res = self.request.get_res(url=endpoint)
#         formated_res = fromstring(res.text)

#         for actor_box in formated_res.xpath('.//div[@class="box actor-box"]'):
#             actors.append(JavActor(
#                                     id = actor_box.xpath("./a/@href")[0].replace("/actors/", ""),
#                                     name = actor_box.xpath("./a/strong")[0].text_content().replace("\n", "").replace(" ", ""),
#                                     names = actor_box.xpath("./a/@title")[0],
#                                     avatar = actor_box.xpath("./a/figure/img/@src")[0],
#                                     type = actor_type
#                                 ))
#         logger.info(actors)
#         return actors
    
#     def get_recommanded_actors(self) -> dict[str, list[JavActor]]:
#         endpoint = f"{self.base_url}/actors"
#         formated_res = fromstring(self.request.get_res(url=endpoint).text)

#         actors: dict[str, list[JavActor]] = {}
#         actor_type_content = formated_res.xpath(".//div[@id='actors']")
#         for index, content in enumerate(formated_res.xpath(".//h3[@class='title is-4 mb-4']")):
#             actors[content.text_content()] = []
#             for actor_box in actor_type_content[index].xpath('.//div[@class="box actor-box"]'):
#                 actors[content.text_content()].append(JavActor(
#                                                                 id = actor_box.xpath("./a/@href")[0].replace("/actors/", ""),
#                                                                 name = actor_box.xpath("./a/strong")[0].text_content().replace("\n", "").replace(" ", ""),
#                                                                 names = actor_box.xpath("./a/@title")[0],
#                                                                 avatar = actor_box.xpath("./a/figure/img/@src")[0]
#                                                             ))
#         logger.info(actors)
#         return actors

#     # def get_movies_by_actor(self, actor_id:str) :
#     #     movies: list[Movie] = []
#     #     # prox
#     #     page_contents = [self.session.get(url=f"{self.base_url}/actors/{actor_id}").text]
#     #     # print(page_contents)
#     #     page_urls = re.findall(r'class="pagination-link.*?" href="(.*?)">[0-9]{1,2}</a>', page_contents[0], re.S)
#     #     for page in page_urls[1:]:
#     #         time.sleep(random.uniform(1,3))
#     #         page_contents.append(self.session.get(url=self.base_url+page).text)

#     #     for page_content in page_contents:
#     #         html = fromstring(page_content)
#     #         for movie_div in html.xpath('//div[contains(@class, "movie-list")]/div'):
#     #             if movie_div.xpath('.//div[@class="tags has-addons"]/span'):
#     #                 movies.append(Movie(movie_id = movie_div.xpath('.//div[@class="video-title"]/strong')[0].text_content(),
#     #                                     movie_title = movie_div.xpath('.//a/@title')[0].strip(),
#     #                                     movie_date = movie_div.xpath('.//div[@class="meta"]')[0].text_content().replace("\n", "").replace(" ", ""),
#     #                                     movie_score = movie_div.xpath('.//span[@class="value"]')[0].text_content().replace("\n", "").replace(" ", "").replace("&nbsp;", "").replace("\xa0", ""),
#     #                                     movie_cover = movie_div.xpath('.//img/@src')[0],
#     #                                     movie_href = movie_div.xpath('.//a/@href')[0]
#     #                                 )
#     #                             )
#     #                 print(movies)
#     #                 break
#     #     return movies
    
#     # def get_movie_detail(self, movie:Movie):
#     #     print(f"获取 {movie.movie_id} 的磁力链接 ... ")
#     #     time.sleep(random.uniform(1,3))
#     #     resp = self.session.get(self.base_url+movie.movie_href)
#     #     if resp.status_code == 200:
#     #         html = fromstring(resp.text)
#     #         # 获取movie 信息
#     #         movie.movie_series = html.xpath('//span[@class="value"]/a[contains(@href, "/series/")]')[0].text_content() if html.xpath('//span[@class="value"]/a[contains(@href, "/series/")]') else ""
#     #         types = []
#     #         for type in html.xpath('//span[@class="value"]/a[contains(@href, "/tags?")]'):
#     #             types.append(type.text_content())
#     #         movie.movie_type = ",".join(types)
#     #         actors = []

#     #         actors_div = html.xpath('//span[@class="value"]/a[contains(@href, "/actors/")]')
#     #         for index, actor_div in enumerate(actors_div):
#     #             sex = html.xpath('//span[@class="value"]/strong[contains(@class, "symbol")]')[index].text_content()
#     #             actors.append(actor_div.text_content()) if sex == "♀" else actors
#     #         movie.movie_actors = ",".join(actors)

#     #         # 获取磁力链接
#     #         links: list[Link] = []
#     #         for link_div in html.xpath('//div[@id="magnets-content"]/div'):
#     #             links.append(Link(  movie_id = movie.movie_id,
#     #                                 link = link_div.xpath('.//a/@href')[0],
#     #                                 link_name = link_div.xpath('.//span[@class="name"]')[0].text_content(),
#     #                                 link_meta = link_div.xpath('.//span[@class="meta"]')[0].text_content().replace("\n", "").replace(" ", "") if link_div.xpath('.//span[@class="meta"]') else "",
#     #                                 link_tags = ",".join(link_div.xpath('.//div[@class="tags"]/span/text()')),
#     #                                 link_date = link_div.xpath('.//span[@class="time"]')[0].text_content() if link_div.xpath('.//span[@class="time"]') else ""
#     #                             )
#     #                         )
#     #         print(links)
#     #         return movie, links
#     #     else:
#     #         print(f"获取 {movie.movie_id} 失败 ... ")
    #         return movie, []

PATH_ROOT = os.path.expanduser("~") + "/.jvav"
PATH_CACHE_JVAV = f"{PATH_ROOT}/.jvav_cache"
if not os.path.exists(PATH_ROOT):
    os.makedirs(PATH_ROOT)

class BaseUtil:
    def __init__(self, proxy_addr="", use_cache=True, expire_after=3600):
        self.log = logging.getLogger(__name__)
        self.proxy_addr = proxy_addr
        self.use_cache = use_cache
        self.proxy_json = None
        self.expire_after = expire_after
        if self.proxy_addr != "":
            self.proxy_json = {"http": proxy_addr, "https": proxy_addr}

    @staticmethod
    def ua_mobile() -> str:
        """返回手机端 UserAgent

        :return str: 手机端 UserAgent
        """
        return UserAgent().android

    @staticmethod
    def ua_desktop() -> str:
        """返回桌面端 UserAgent

        :return str: 桌面端 UserAgent
        """
        return UserAgent(platform="windows").random

    @staticmethod
    def ua() -> str:
        """随机返回 UserAgent

        :return str: UserAgent
        """
        return UserAgent().random

    def _inner_send_req(
        self, url: str, session, headers=None, m=0, **args
    ) -> Union[Tuple[int, None], Tuple[int, Any]]:
        if not headers:
            headers = {"user-agent": self.ua()}
        try:
            methods = {
                0: session.get,
                1: session.post,
                2: session.delete,
                3: session.put,
            }
            if m in methods:
                if self.proxy_json:
                    resp = methods[m](
                        url, proxies=self.proxy_json, headers=headers, **args
                    )
                else:
                    resp = methods[m](url, headers=headers, **args)
                if resp.status_code != 200:
                    return 404, None
                return 200, resp
            else:
                return 502, None
        except Exception as e:
            self.log.error(f"BaseUtil: 访问 {url}: {e}")
            return 502, None

    def send_req(
        self, url: str, headers=None, m=0, **args
    ) -> Tuple[int, requests.Response]:
        """发送请求

        :param str url: 地址
        :param dict headers: 请求头, 默认使用随机请求头
        :param int m: 请求方法, 默认为 get(0), 其他为 post(1), delete(2), put(3)
        :param dict args: 其他 requests 参数
        :return tuple[int, requests.Response] 状态码和请求返回值
        关于状态码:
        200: 成功
        404: 未找到
        502: 后台/网络问题
        """
        if self.use_cache:
            with requests_cache.CachedSession(
                cache_name=PATH_CACHE_JVAV, expire_after=self.expire_after
            ) as session:
                return self._inner_send_req(url, session, headers, m, **args)
        else:
            with requests.Session() as session:
                return self._inner_send_req(url, session, headers, m, **args)

    @staticmethod
    def get_soup(resp: requests.Response) -> BeautifulSoup:
        """从请求结果得到 soup

        :param requests.Response resp: 请求结果
        :return BeautifulSoup
        """
        return BeautifulSoup(resp.text, "lxml")

    @staticmethod
    def write_html(resp: requests.Response):
        with open(f"./tmp.html", "w") as f:
            f.write(resp.text)

class MagnetUtil:
    @staticmethod
    def get_nice_magnets(magnets: list, prop: str, expect_val: any) -> list:
        """过滤磁链列表

        :param list magnets: 要过滤的磁链列表
        :param str prop: 过滤属性
        :param any expect_val: 过滤属性的期望值
        :return list: 过滤后的磁链列表
        """
        # 已经无法再过滤
        if len(magnets) == 0:
            return []
        if len(magnets) == 1:
            return magnets
        magnets_nice = []
        for magnet in magnets:
            if magnet[prop] == expect_val:
                magnets_nice.append(magnet)
        # 如果过滤后已经没了, 返回原来磁链列表
        if len(magnets_nice) == 0:
            return magnets
        return magnets_nice

    @staticmethod
    def sort_magnets(magnets: list) -> list:
        """根据大小排列磁链列表

        :param list magnets: 磁链列表
        :return list: 排列好的磁链列表
        """
        # 统一单位为 MB
        for magnet in magnets:
            magnet["size_no_unit"] = -1
            size = magnet["size"].lower().replace("gib", "gb").replace("mib", "mb")
            gb_idx = size.find("gb")
            mb_idx = size.find("mb")
            if gb_idx != -1:  # 单位为 GB
                magnet["size_no_unit"] = float(size[:gb_idx]) * 1024
            elif mb_idx != -1:  # 单位为 MB
                magnet["size_no_unit"] = float(size[:mb_idx])
        # magnets = list(filter(lambda m: m["size_no_unit"] != -1, magnets))
        # 根据 size_no_unit 大小排序
        magnets = sorted(magnets, key=lambda m: m["size_no_unit"], reverse=True)
        return magnets

class JavDbUtil(BaseUtil):
    BASE_URL = "https://javdb.com"
    BASE_PARAM_NICE_AVS_OF_STAR = "?sort_type=1"
    PAT_SCORE = re.compile(r"(\d+\.?\d+)分")

    def __init__(
        self,
        proxy_addr="",
        use_cache=True,
        max_home_page_count=100,
        max_new_avs_count=8,
        base_url=BASE_URL,
    ):
        """初始化

        :param str proxy_addr: 代理服务器地址, 默认为 ''
        :param bool use_cache: 是否使用缓存, 默认为 True
        :param int max_home_page_count: 主页最大爬取页数, 默认为 100 页
        :param int max_new_avs_count: 获取最新 AV 数量, 默认为 8 部
        :param str base_url: 基础地址, 默认为 BASE_URL
        """
        super().__init__(proxy_addr, use_cache)
        self.base_url = base_url
        self.base_url_new_av = self.base_url + "/?vft=1&vst=1"
        self.base_url_search = self.base_url + "/search?q="
        self.base_url_video = self.base_url + "/v/"
        self.base_url_actor = self.base_url + "/actors/"
        self.base_url_search_star = self.base_url + "/search?f=actor&q="
        self.max_home_page_count = max_home_page_count
        self.max_new_avs_count = max_new_avs_count

    def get_max_page(self, url: str) -> Union[Tuple[int, None], Tuple[int, int]]:
        """获取最大页数

        :param str url: 页面地址
        :return tuple[int, int]: 状态码和最大页数
        """
        code, resp = self.send_req(url)
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            if pagination_list := soup.find(class_="pagination-list"):
                try:
                    last_page = int(
                        pagination_list.find_all("li")[-1].a.text
                    )
                except:
                    temp_page = int(
                        pagination_list.find_all("li")[-2].a.text
                    )
                    return self.get_max_page(re.sub("page=.+", f"page={temp_page}", url))
            else:
                last_page = 1
            return 200, last_page
        except Exception as e:
            self.log.error(f"JavDbUtil: 从 {url} 获取最大页数: {e}")
            return 200, 1

    def get_new_ids(self) -> Tuple[int, any]:
        """获取最新的番号列表

        :return Tuple[int, list]: 状态码和番号列表
        """
        return self.get_ids_from_page(self.base_url_new_av)

    def get_ids_from_page(
        self, url: str
    ) -> Union[Tuple[int, None], Tuple[int, List[Any]]]:
        """从页面 url 获取番号列表

        :param str url: 首页/搜索页
        :return Tuple[int, list]: 状态码和番号列表
        """
        code, resp = self.send_req(url=url)
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            items = soup.find_all(class_="item")
            ids = [
                item.find(class_="video-title").strong.text.strip() for item in items
            ]
            if not ids:
                return 404, None
            return 200, ids
        except Exception as e:
            self.log.error(f"JavDbUtil: 从页面获取番号列表: {e}")
            return 404, None
        
    def get_id_details_from_page(
        self, url: str
    ) -> Union[Tuple[int, None], Tuple[int, List[Any]]]:
        """从页面 url 获取番号列表

        :param str url: 首页/搜索页
        :return Tuple[int, list]: 状态码和番号列表
        """
        code, resp = self.send_req(url=url)
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            items = soup.find_all(class_="item")
            id_details = []
            for item in items:
                if score_search:=re.search("(\d+\.*\d*)(分, 由.+人評價)", item.find(class_="value").text.strip()):
                    score = score_search.group(1).strip()
                else:
                    score = "NA"

                if tag_node := item.find(class_="tags has-addons").find("span"):
                    tag = tag_node.text.strip()
                else:
                    tag = ""
                
                id_details.append({
                    "id": item.find(class_="video-title").strong.text.strip(),
                    "jav_id": item.find("a")["href"].split("/")[-1],
                    "date": item.find(class_="meta").text.strip(),
                    "title": item.find("a")["title"].strip(),
                    "score": score,
                    "img": item.find("img")["src"],
                    "tag": tag
                })

            # ids = [
            #     item.find(class_="video-title").strong.text.strip() for item in items
            # ]
            # if not ids:
            #     return 404, None
            return 200, id_details
        except Exception as e:
            self.log.error(f"JavDbUtil: 从页面获取番号列表: {e}")
            return 404, None

    def get_star_page_by_star_name(
        self, star_name
    ) -> Union[Tuple[int, None], Tuple[int, str]]:
        code, resp = self.send_req(url=self.base_url_search_star + star_name)
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            url = soup.find(class_="actor-box").find("a").attrs["href"]
            if not url:
                return 404, None
            return 200, f"{self.base_url}{url}"
        except Exception as e:
            self.log.error(f"JavDbUtil: 获取预览图片: {e}")
            return 404, None

    def fuzzy_search_stars(
        self, text
    ) -> Union[Tuple[int, None], Tuple[int, List[Any]]]:
        """模糊搜索演员

        :param str text: 演员名称
        :return Tuple[int, list]: 状态码和演员列表
        """
        code, resp = self.send_req(url=self.base_url_search_star + text)
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            actor_boxs = soup.find_all(class_="actor-box")
            names = [box.find("a")["title"] for box in actor_boxs]
            if not names:
                return 404, None
            names = [name.split(",")[0] for name in names]
            names = list(set(names))
            return 200, names
        except Exception as e:
            self.log.error(f"JavDbUtil: 模糊搜索演员: {e}")
            return 404, None

    def get_id_by_star_name(
        self, star_name: str, page=-1
    ) -> Union[Tuple[int, None], Tuple[int, Any]]:
        """根据演员名称获取一个番号

        :param str star_name: 演员名称
        :param int page: 用于指定爬取哪一页的数据, 默认值为 -1, 表示随机获取某一页
        :return tuple[int, str]: 状态码和番号
        """
        code, ids = self.get_ids_by_star_name(star_name, page)
        if code != 200:
            return code, None
        return 200, random.choice(ids)

    def get_ids_by_star_name(
        self, star_name: str, page=-1
    ) -> Union[Tuple[Any, None], Tuple[int, Any], Tuple[int, None]]:
        """根据演员名称获取一批番号

        :param str star_name: 演员名称
        :param int page: 用于指定爬取哪一页的数据, 默认值为 -1, 表示随机获取某一页
        :return tuple[int, list]: 状态码和番号
        """
        code, base_page_url = self.get_star_page_by_star_name(star_name)
        if code != 200:
            return code, None
        try:
            if page != -1:
                url = f"{base_page_url}?page={page}"
            else:
                code, max_page = self.get_max_page(base_page_url)
                if code != 200:
                    return code, None
                url = f"{base_page_url}?page={random.randint(1, max_page)}"
            code, ids = self.get_ids_from_page(url)
            if code != 200:
                return code, None
            return 200, ids
        except Exception as e:
            self.log.error(f"JavDbUtil: 根据演员名称获取一个番号: {e}")
            return 404, None
    
    def get_id_details_by_star_id(
        self, star_id: str, page=-1
    ) -> Union[Tuple[Any, None], Tuple[int, Any], Tuple[int, None]]:
        """根据演员id获取番号

        :param str star_name: 演员名称
        :param int page: 用于指定爬取哪一页的数据, 默认值为 -1, 表示随机获取全部
        :return tuple[int, list]: 状态码和番号
        """
        base_page_url = self.base_url_actor+star_id
        try:
            if page != -1:
                urls = [f"{base_page_url}?page={page}"]
            else:
                code, max_page = self.get_max_page(base_page_url)
                if code != 200:
                    return code, None
                urls = [f"{base_page_url}?page={page}" for page in range(1, max_page+1)]
            id_details = []
            for url in urls:
                code, id_detail = self.get_id_details_from_page(url)
                if code == 200:
                    id_details += id_detail
            return 200, id_details
        except Exception as e:
            self.log.error(f"JavDbUtil: 根据演员id获取番号: {e}")
            return 404, None

    def get_new_ids_by_star_name(
        self, star_name: str
    ) -> Union[Tuple[Any, None], Tuple[int, Any], Tuple[int, None]]:
        """根据演员名字获取最新番号列表

        :param str star_name: 演员名称
        :return Tuple[int, list]: 状态码和番号列表
        """
        code, url = self.get_star_page_by_star_name(star_name)
        if code != 200:
            return code, None
        try:
            code, ids = self.get_ids_from_page(url)
            if code != 200:
                return code, None
            return 200, ids[: self.max_new_avs_count]
        except Exception as e:
            self.log.error(f"JavDbUtil: 根据演员名字获取最新番号列表: {e}")
            return 404, None

    def get_nice_avs_by_star_name(
        self, star_name: str, cookie: str
    ) -> Union[
        Tuple[Any, None], Tuple[int, None], Tuple[int, List[Dict[str, Union[str, Any]]]]
    ]:
        """根据演员名字获取高分番号列表(需要登录)

        :param str star_name: 演员名字
        :param str cookie: 该方法需要登录，cookie 中的 _jdb_session 为必须值
        :return Tuple[int, list]: 状态码和番号列表
        番号列表单个对象结构:
        {
            'rate': rate, # 评分
            'id': id # 番号
        }
        """
        code, base_page_url = self.get_star_page_by_star_name(star_name)
        if code != 200:
            return code, None
        url = f"{base_page_url}{self.BASE_PARAM_NICE_AVS_OF_STAR}"
        code, resp = self.send_req(
            url=url, headers={"cookie": cookie, "user-agent": self.ua_desktop()}
        )
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            items = soup.find_all(class_="item")
            res = []
            for item in items:
                try:
                    res.append(
                        {
                            "rate": self.PAT_SCORE.findall(
                                item.find(class_="score").text
                            )[0],
                            "id": item.find(class_="video-title").strong.text.strip(),
                        }
                    )
                except Exception:
                    pass
            if not res:
                return 404, None
            return 200, res
        except Exception as e:
            self.log.error(f"JavDbUtil: 从页面获取番号列表: {e}")
            return 404, None

    def get_javdb_id_by_id(self, id: str) -> Union[Tuple[int, None], Tuple[int, Any]]:
        """通过番号获取 JavDB 内部 ID

        :param id: 番号
        :return: tuple[int, str] 状态码和 JavDB 内部 ID
        """
        code, resp = self.send_req(url=self.base_url_search + id)
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            items = soup.find_all(class_="item")
            for item in items:
                if item.find(class_="video-title").strong.text.strip() == id.upper():
                    return 200, item.find("a")["href"].split("/")[-1]
            return 404, None  # if there is no correct result, return 404
        except Exception as e:
            self.log.error(f"JavDbUtil: 通过番号获取JavDB内部ID: {e}")
            return 404, None

    def get_javdb_ids_from_page(
        self, url: str
    ) -> Union[Tuple[int, None], Tuple[int, List[Any]]]:
        """从页面 url 获取 JavDB 的 ID 列表

        :param url: 首页/搜索页
        :return: Tuple[int, list]: 状态码和 JavDB 的 ID 列表
        """
        code, resp = self.send_req(url=url)
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            items = soup.find_all(class_="item")
            ids = [item.find("a")["href"].split("/")[-1] for item in items]
            if not ids:
                return 404, None
            return 200, ids
        except Exception as e:
            self.log.error(f"JavDbUtil: 从页面获取 JavDB 内部 ID 列表: {e}")
            return 404, None

    def get_id_from_home(self) -> Union[Tuple[Any, None], Tuple[int, Any]]:
        """从主页获取一个番号(随机选取) 从首页获取 ID 或 JavDB ID

        :return Tuple[int, str]: 状态码和番号
        """
        code, resp = self.get_ids_from_page(url=self.base_url)
        if code != 200:
            return code, None
        else:
            return 200, random.choice(resp)

    def get_javdb_id_from_home(self) -> Union[Tuple[Any, None], Tuple[int, Any]]:
        """从主页获取一个 JavDB 内部 ID (随机选取)

        :return Tuple[int, str]: 状态码和 JavDB 内部 ID
        """
        code, resp = self.get_javdb_ids_from_page(url=self.base_url)
        if code != 200:
            return code, None
        else:
            return 200, random.choice(resp)

    def get_ids_from_home(self) -> Union[Tuple[Any, None], Tuple[int, Any]]:
        """从主页获取全部番号

        :return Tuple[int, list]: 状态码和番号列表
        """
        code, resp = self.get_ids_from_page(url=self.base_url)
        if code != 200:
            return code, None
        else:
            return 200, resp

    def get_javdb_ids_from_home(self) -> Union[Tuple[Any, None], Tuple[int, Any]]:
        """从主页获取全部 JavDB 内部 ID

        :return Tuple[int, list]: 状态码和 JavDB 内部 ID 列表
        """
        code, resp = self.get_javdb_ids_from_page(url=self.base_url)
        if code != 200:
            return code, None
        else:
            return 200, resp

    def get_ids_by_tag(self, tag: str) -> Tuple[int, list]:
        """根据标签获取番号列表

        :param str tag: 标签
        :return Tuple[int, list]: 状态码和番号列表
        """
        url = f"{self.base_url_search}{tag}"
        return self.get_ids_from_page(url)

    def get_javdb_ids_by_tag(self, tag: str) -> Tuple[int, list]:
        """根据标签获取 JavDB 列表

        :param str tag: 标签
        :return Tuple[int, list]: 状态码和番号列表
        """
        url = f"{self.base_url_search}{tag}"
        return self.get_javdb_ids_from_page(url)

    def get_cover_by_id(self, id: str) -> Union[Tuple[int, None], Tuple[int, Any]]:
        """根据番号获取封面

        :param str id: 番号
        :return Tuple[int, str]: 状态码和封面
        """
        code, resp = self.send_req(url=self.base_url_search + id)
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            items = soup.find_all(class_="item")
            for item in items:
                if item.find(class_="video-title").strong.text.strip() == id.upper():
                    return 200, item.find("img")["src"]
            else:
                return 404, None
        except Exception as e:
            self.log.error(f"JavDbUtil: 通过番号获取封面: {e}")
            return 404, None

    def get_cover_by_javdb_id(
        self, javdb_id: str
    ) -> Union[Tuple[int, None], Tuple[int, Union[str, Any]]]:
        """通过 JavDB ID 获取封面

        :param str javdb_id: JavDB 内部 ID
        :return Tuple[int, str]: 状态码和封面
        """
        code, resp = self.send_req(url=self.base_url_video + javdb_id)
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            cover = soup.find(class_="column column-video-cover")
            if not cover:
                return 404, None
            return 200, cover.find("img")["src"]
        except Exception as e:
            self.log.error(f"JavDbUtil: 通过JavDB ID获取封面: {e}")
            return 404, None

    def get_pv_by_id(
        self, id: str
    ) -> Union[Tuple[Any, None], Tuple[int, None], Tuple[int, Union[str, Any]]]:
        code, j_id = self.get_javdb_id_by_id(id)
        if code != 200:
            return code, None
        code, resp = self.send_req(url=self.base_url_video + j_id)
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            url = soup.find(id="preview-video").find("source").attrs["src"]
            if not url:
                return 404, None
            if "http" not in url:
                url = f"https:{url}"
            return 200, url
        except Exception as e:
            self.log.error(f"JavDbUtil: 获取预览视频: {e}")
            return 404, None

    def get_samples_by_id(
        self, id: str
    ) -> Union[Tuple[Any, None], Tuple[int, None], Tuple[int, List[Any]]]:
        code, j_id = self.get_javdb_id_by_id(id)
        if code != 200:
            return code, None
        code, resp = self.send_req(url=self.base_url_video + j_id)
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            img_tags = soup.find_all(class_="tile-item")
            if not img_tags:
                return 404, None
            return 200, [t.attrs["href"] for t in img_tags]
        except Exception as e:
            self.log.error(f"JavDbUtil: 获取预览图片: {e}")
            return 404, None

    def get_av_by_javdb_id(
        self,
        javdb_id: str,
        is_nice: bool,
        is_uncensored: bool,
        sex_limit: bool = False,
        magnet_max_count=10,
    ) -> Tuple[int, any]:
        """通过 JavDB ID 获取 av

        :param javdb_id: JavDB 内部 ID
        :param bool is_nice: 是否过滤出高清，有字幕磁链
        :param bool is_uncensored: 是否过滤出无码磁链
        :param bool sex_limit: 是否只获取女优信息
        :param int magnet_max_count: 过滤后磁链的最大数目, 默认为 10
        :return Tuple[int, any]: 状态码和 av
        av格式:
        {
            'id': '',       # 番号
            'date': '',     # 发行日期
            'title': '',    # 标题
            'title_cn': '', # 中文标题
            'img': '',      # 封面地址
            'duration': '', # 时长(单位: 分钟)
            'producer': '', # 片商
            'publisher': '',# 发行商
            'series': '',   # 系列
            'score': '',   # 评分
            'tags': [],     # 标签
            'stars': [],    # 演员
            'magnets': [],  # 磁链
            'url': '',      # 地址
        }
        磁链格式:
        {
            'link': '', # 链接
            'size': '', # 大小
            'hd': '0',  # 是否高清 0 否 | 1 是
            'zm': '0',  # 是否有字幕 0 否 | 1 是
            'uc': '0',  # 是否未经审查 0 否 | 1 是
            'size_no_unit': 浮点值 # 去除单位后的大小值, 用于排序, 当要求过滤磁链时会存在该字段
        }
        演员格式:
        {
            'name': '', # 演员名称
            'id': ''    # 演员编号
            'sex': ''   # 演员性别
        }
        """
        code, resp = self.send_req(url=self.base_url_video + javdb_id)
        if code != 200:
            return code, None
        try:
            av = {
                "id": "",
                "date": "",
                "img": "",
                "title": "",
                "title_cn": "",
                "duration": "",
                "producer": "",
                "publisher": "",
                "series": "",
                "score": "",
                "tags": [],
                "stars": [],
                "magnets": [],
                "url": self.base_url_video + javdb_id,
            }
            soup = self.get_soup(resp)
            # 获取元信息
            title_cn = soup.find("strong", {"class": "current-title"})
            title = soup.find("span", {"class": "origin-title"})
            if not title:
                title, title_cn = title_cn, ""
            av["title_cn"] = title_cn.text.strip() if title_cn else ""
            av["title"] = title.text.strip() if title else ""
            av["img"] = soup.find("div", {"class": "column column-video-cover"}).find("img")["src"]
            # 由于nav栏会因为实际信息不同而导致行数不同，所以只能用循环的方式检索信息
            metainfos = soup.find("nav", {"class": "panel movie-panel-info"}).find_all(
                "div", {"class": "panel-block"}
            )
            for info in metainfos:  # 遍历nav栏所有信息
                text = unicodedata.normalize("NFKD", re.sub("[\n ]", "", info.text))
                if re.search("番號:.+", text):
                    av["id"] = re.search("(番號: )(.+)", text).group(2).strip()
                elif re.search("日期:.+", text):
                    av["date"] = re.search("(日期: )(.+)", text).group(2).strip()
                elif re.search("\d+(分鍾)", text):
                    av["duration"] = int(re.search("(\d+)(分鍾)", text).group(1))
                elif re.search("片商:.+", text):
                    av["producer"] = re.search("(片商: )(.+)", text).group(2).strip()
                elif re.search("發行:.+", text):
                    av["publisher"] = re.search("(發行: )(.+)", text).group(2).strip()
                elif re.search("系列:.+", text):
                    av["series"] = re.search("(系列: )(.+)", text).group(2).strip()
                elif re.search("類別:.+", text):
                    av["tags"] = re.search("(類別: )(.+)", text).group(2).split(", ")
                elif re.search("評分:.+", text):
                    av["score"] = (
                        re.search("(評分: +)(\d+\.*\d*)(分.+)", text).group(2).strip()
                    )
                elif re.search("演員:.+", text):
                    actor_info = info.find_all(("a", "strong"))[1:]
                    for a in range(len(actor_info) // 2):
                        actor = {
                            "name": actor_info[a * 2].text.strip(),
                            "id": actor_info[a * 2]["href"].split("/")[-1],
                            "sex": (
                                "女"
                                if actor_info[a * 2 + 1].text.endswith("♀")
                                else "男"
                            ),
                        }
                        if not (sex_limit and actor["sex"] == "男"):
                            av["stars"].append(actor)
            # 获取磁链
            magnet_list = soup.find_all(
                "div", {"class": "item columns is-desktop"}
            ) + soup.find_all("div", {"class": "item columns is-desktop odd"})
            for link in magnet_list:
                magnet = {
                    "link": link.find("a")["href"],
                    "hd": "0",
                    "zm": "0",
                    "uc": "0",
                    "size": "0",
                }
                # 获取大小
                size = link.find("span", {"class": "meta"})
                if size:
                    magnet["size"] = size.text.strip().split(",")[0]
                # 检查是否为uc
                title = link.find("span", {"class": "name"}).text
                if any(
                    k in title
                    for k in [
                        "-U",
                        "无码",
                        "無碼",
                        "无码流出",
                        "無碼流出",
                        "无码破解",
                        "無碼破解",
                        "uncensored",
                        "Uncensored",
                    ]
                ):
                    magnet["uc"] = "1"
                # 检查tag
                tags_elements = link.find("div", {"class": "tags"})
                if tags_elements:
                    tags_contents = tags_elements.findAll("span")
                    for i in tags_contents:
                        if i.text.strip() == "高清":
                            magnet["hd"] = "1"
                        elif i.text.strip() == "字幕":
                            magnet["zm"] = "1"
                av["magnets"].append(magnet)
            if is_uncensored:
                av["magnets"] = MagnetUtil.get_nice_magnets(
                    av["magnets"], "uc", expect_val="1"
                )
            if is_nice:
                magnets = av["magnets"]
                magnets = MagnetUtil.get_nice_magnets(
                    magnets, "hd", expect_val="1"
                )  # 过滤高清
                magnets = MagnetUtil.get_nice_magnets(
                    magnets, "zm", expect_val="1"
                )  # 过滤有字幕
                magnets = MagnetUtil.sort_magnets(magnets)  # 从大到小排序
                magnets = magnets[0:magnet_max_count]
                av["magnets"] = magnets
            return 200, av
        except Exception as e:
            self.log.error(f"JavDbUtil: 获取av信息: {e}")
            return 404, None

    def get_av_by_id(
        self,
        id: str,
        is_nice: bool,
        is_uncensored: bool,
        sex_limit: bool = False,
        magnet_max_count=10,
    ) -> Tuple[int, any]:
        """通过 javdb 获取番号对应 av

        :param str id: 番号
        :param bool is_nice: 是否过滤出高清，有字幕磁链
        :param bool is_uncensored: 是否过滤出无码磁链
        :param int magnet_max_count: 过滤后磁链的最大数目, 默认为 10
        :return Tuple[int, dict]: 状态码和 av
        av格式:
        {
            'id': '',       # 番号
            'date': '',     # 发行日期
            'title': '',    # 标题
            'title_cn': '', # 中文标题
            'img': '',      # 封面地址
            'duration': '', # 时长(单位: 分钟)
            'producer': '', # 片商
            'publisher': '',# 发行商
            'series': '',   # 系列
            'score': '',   # 评分
            'tags': [],     # 标签
            'stars': [],    # 演员
            'magnets': [],  # 磁链
            'url': '',      # 地址
        }
        磁链格式:
        {
            'link': '', # 链接
            'size': '', # 大小
            'hd': '0',  # 是否高清 0 否 | 1 是
            'zm': '0',  # 是否有字幕 0 否 | 1 是
            'uc': '0',  # 是否未经审查 0 否 | 1 是
            'size_no_unit': 浮点值 # 去除单位后的大小值, 用于排序, 当要求过滤磁链时会存在该字段
        }
        演员格式:
        {
            'name': '', # 演员名称
            'id': ''    # 演员编号
            'sex': ''   # 演员性别
        }
        """
        code, j_id = self.get_javdb_id_by_id(id)
        return (
            self.get_av_by_javdb_id(
                j_id, is_nice, is_uncensored, sex_limit, magnet_max_count
            )
            if code == 200
            else (code, None)
        )
    
    def get_recommanded_actors(self) -> dict[str, list[JavActor]]:
        endpoint = f"{self.base_url}/actors"
        formated_res = fromstring(self.send_req(url=endpoint)[1].text)

        actors: dict[str, list[JavActor]] = {}
        actor_type_content = formated_res.xpath(".//div[@id='actors']")
        for index, content in enumerate(formated_res.xpath(".//h3[@class='title is-4 mb-4']")):
            actors[content.text_content()] = []
            for actor_box in actor_type_content[index].xpath('.//div[@class="box actor-box"]'):
                actors[content.text_content()].append(JavActor(
                                                                id = actor_box.xpath("./a/@href")[0].replace("/actors/", ""),
                                                                name = actor_box.xpath("./a/strong")[0].text_content().replace("\n", "").replace(" ", ""),
                                                                names = actor_box.xpath("./a/@title")[0],
                                                                avatar = actor_box.xpath("./a/figure/img/@src")[0]
                                                            ))
        return actors

    def get_actors_by_type(self, actor_type: str, page: int) -> list[JavActor]|None:
        """根据分类获取演员信息

        Args:
            actor_type (str): 演员类型, censored/uncensored/western

        Returns:
            list[JavActor]: 演员信息
        """
        actors: list[JavActor] = []

        if page == 1:
            endpoint = f"{self.base_url_actor}{actor_type}"
        else:
            endpoint = f"{self.base_url_actor}{actor_type}?page={page}"

        code, resp = self.send_req(url=endpoint)
        if code != 200:
            return None
        
        try:
            soup = self.get_soup(resp)
            actor_boxes = soup.find_all(class_="box actor-box")
            if actor_boxes:
                for actor_box in soup.find_all(class_="box actor-box"):
                    actors.append(JavActor(
                                            id = actor_box.find("a").attrs["href"].split("/")[-1],
                                            name = actor_box.find("strong").text.strip(),
                                            names = actor_box.find("a").attrs["title"],
                                            avatar = actor_box.find("img").attrs["src"]
                                        ))
                return actors
            else:
                return []
        except:
            return None

        res = self.request.get_res(url=endpoint)
        formated_res = fromstring(res.text)

        for actor_box in formated_res.xpath('.//div[@class="box actor-box"]'):
            actors.append(JavActor(
                                    id = actor_box.xpath("./a/@href")[0].replace("/actors/", ""),
                                    name = actor_box.xpath("./a/strong")[0].text_content().replace("\n", "").replace(" ", ""),
                                    names = actor_box.xpath("./a/@title")[0],
                                    avatar = actor_box.xpath("./a/figure/img/@src")[0],
                                    type = actor_type
                                ))
        logger.info(actors)
        return actors


if __name__ == "__main__":
    # cookie = "list_mode=h; theme=auto; locale=zh; over18=1; _rucaptcha_session_id=35779bab0d8dd91cdee36f8f4d4e205c; cf_clearance=XILyQozo1jBmci0f1JuGfWevBhIoaH7RrlcH5Iz0gYg-1718535847-1.0.1.1-IpKnxjzFbR4n5EJXo57Oa2Oxkwyo5SClv4vqsdrr21c3WPxbkuWGR_PasJRoW86fy1bovWbIE0SALlhQ_cNDMA; _jdb_session=w7FLcQPvdXNcNN5txHhAwnRnuSr8Ox5TZ4HaLVuEs24fN0CSn1vfhfQJWoh4Gb1UtkRQVldq9%2BUJVWnwSOGTaFgIE0oVhTtCkXIqT%2F3l8NPJwuFJOEJYruilwTid%2B1gh5wDJx2nlnRpxpekpPVBiWbd5rgp8B6J81I1%2F4%2BTgE36zWreBKQf%2BXdiAkSEeVH0gBAJQq7IdWYPEZ8urXoQ647Om%2FyAqrcmuuzPkdmAR%2BOBq%2BGRN6RoozR1EAzBOZQIKNgrxZ5x%2BH5G%2BQMGtDNWkOPcx0UVH5PZq2eaAlyx0JNEiaoLrTHx1C9qHIgGh6F85lkyfFiEn4m1%2BN8TTWL73vdDaBX5VPV70iLS2CDF%2BluYTxn%2FCcPlCsW4ZXamNLb9WvbA%3D--Mt5801I7xPIjot4b--nUb2ZLk6p1AHC0g8WNTarA%3D%3D"
    # javdb = JavDB("https://javdb.com")
    # javdb.get_movie_detail(javdb.get_movies_by_actor("RJM8")[0])
    jav_util = JavDbUtil("http://192.168.3.65:7890")
    # print(jav_util.get_av_by_id("PFES-107", False, False))
    code, ids = jav_util.get_id_details_by_star_id("65v5Q")
    print(ids)
    # for id in ids:
    #     print(jav_util.get_av_by_id(id, True, True)[1])
    # print(jav_util.get_id_details_by_star_id("三上悠亚"))
    # proxies = {
    #         "http": "http://192.168.3.65:7890",
    #         "https": "http://192.168.3.65:7890"
    #     }
    # contetn = requests.get("https://www.google.com", proxies=proxies)
    # print(contetn)
    # # javdb.check_login_status()
    # exist_movies = get_exist_movies("192.168.3.65:8098", "37dc3a04bd0d4fe6a0f0eb5f216806a1", "日本")
    # javdb.get_actor_movies("枫可怜", exist_movies)
    # javdb.get_actor_movies("桥本有菜", exist_movies)
    # javdb.get_actor_movies("明里柚", exist_movies)
    # javdb.get_actor_movies("河北彩花", exist_movies)
    # # javdb.get_actor_movies("三上悠亚", exist_movies)
    # javdb.get_actor_movies("桃乃木香奈", exist_movies)
    # javdb.get_actor_movies("葵司", exist_movies)
    # javdb.get_actor_movies("凉森玲梦", exist_movies)
    # # javdb.get_actor_movies("山岸逢花", exist_movies)
    # # javdb.get_actor_movies("Melody Marks", exist_movies)
    # javdb.get_actor_movies("野野浦暖", exist_movies)
    # javdb.get_actor_movies("希岛爱理", exist_movies)

    # javdb.get_actor_movies("石川澪", exist_movies)
    # javdb.get_actor_movies("小岛南", exist_movies)
    # pass