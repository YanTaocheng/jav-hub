import traceback
import requests
import json
import logging
import re
from datetime import datetime
from typing import Optional, Union
import urllib.request as url_request

logger = logging.getLogger("emby_util")

class Emby:
    def __init__(self, host: str, api_key: str):
        if host:
            try:
                response = url_request.urlopen(host, timeout=8)
                if response.status == 200:
                    self.emby_host = host
                else:
                    self.emby_host = ""
            except:
                self.emby_host = ""
                logger.error(f"Emby服务器: {host}无法访问")
            self.emby_api_key = api_key

    def get_system_info(self):
        """
        获得服务器信息
        """
        if not self.emby_host or not self.emby_api_key:
            return {}
        
        url = f"{self.emby_host}/System/Info"
        params = {
            'api_key': self.emby_api_key
        }
        try:
            res = requests.get(url, params)
            if res:
                return res.json()
            else:
                logger.warning(f"System/Info 未获取到返回数据")
        except Exception as e:
            logger.warning(f"连接System/Info出错：" + str(e))
        return {}
    
    def get_user_count(self) -> int:
        """
        获得用户数量
        """
        if not self.emby_host or not self.emby_api_key:
            return 0
        
        url = f"{self.emby_host}/emby/Users/Query"
        params = {
            'api_key': self.emby_api_key
        }
        try:
            res = requests.get(url, params)
            if res.status_code==200:
                return res.json().get("TotalRecordCount")
            else:
                logger.error(f"Users/Query 未获取到返回数据")
                return 0
        except Exception as e:
            logger.error(f"连接Users/Query出错：" + str(e))
            return 0
        
    def get_user_id(self) -> list:
        """
        获得用户id
        """
        if not self.emby_host or not self.emby_api_key:
            return []
        
        url = f"{self.emby_host}/emby/user_usage_stats/user_list"
        params = {
            'api_key': self.emby_api_key
        }
        try:
            res = requests.get(url, params)
            if res.status_code==200:
                return res.json()
            else:
                # logger.warning(f"user_usage_stats/user_list 未获取到返回数据")
                return []
        except Exception as e:
            # logger.warning(f"连接user_usage_stats/user_list出错：" + str(e))
            return []
        
    def get_librarys(self, username: str|None = None, hidden: bool = False):
        """
        获取Emby媒体库列表
        """
        if not self.emby_host or not self.emby_api_key:
            return []
        
        user = self.get_admin_user()

        url = f"{self.emby_host}/emby/Users/{user}/Views"
        params = {"api_key": self.emby_api_key}
        try:
            res = requests.get(url, params)
            if res.status_code == 200 and res:
                return res.json().get("Items", [])
            else:
                logger.warning(f"User/Views 未获取到返回数据")
                return []
        except Exception as e:
            logger.warning(f"连接User/Views 出错：" + str(e))
            return []
        
    def get_library_items(self, library_id: str, sorted: str="SortName"):
        # 获取指定媒体库的内容
        if not self.emby_host or not self.emby_api_key:
            return []
        url = f"{self.emby_host}/emby/Items"
        params = {
            "ParentId": library_id,
            "api_key": self.emby_api_key,
            "Recursive": "true",
            "IncludeItemTypes": "Series,Movie",
            "Fields": "DateCreated",
            "ImageTypeLimit": 1,
            "SortBy": f"{sorted},SortName" if sorted not in ["SortName", "Random"] else sorted,
            "SortOrder": "Descending" if sorted not in ["SortName", "Random"] else "Ascending"
        }
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json().get("Items", [])
            else:
                logger.warning(f"emby/Items 未获取到返回数据")
                return []
        except Exception as e:
            logger.warning(f"连接emby/Items 出错：" + str(e))
            return []
        
    def get_admin_user(self) -> str:
        """
        获得用户id
        """
        if not self.emby_host or not self.emby_api_key:
            return ""
        
        url = f"{self.emby_host}/Users"
        params = {
            'api_key': self.emby_api_key
        }
        try:
            res = requests.get(url, params)
            if res.status_code==200:
                users = res.json()
                # 查询管理员
                for user in users:
                    if user.get("Policy", {}).get("IsAdministrator"):
                        return user.get("Id")
            else:
                logger.warning(f"Users 未获取到返回数据")
                return ""
        except Exception as e:
            logger.warning(f"连接Users出错：" + str(e))
            return ""
        
    def get_tv_items(self, parent: Union[str, int]) -> dict:
        """
        获取媒体服务器项目列表，支持分页和不分页逻辑，默认不分页获取所有数据

        :param parent: 媒体库ID，用于标识要获取的媒体库
        :param start_index: 起始索引，用于分页获取数据。默认为 0，即从第一个项目开始获取
        :param limit: 每次请求的最大项目数，用于分页。如果为 None 或 -1，则表示一次性获取所有数据，默认为 -1

        :return: 返回一个生成器对象，用于逐步获取媒体服务器中的项目
        """
        if not parent or not self.emby_host or not self.emby_api_key:
            return []
        url = f"{self.emby_host}/emby/Shows/{parent}/Episodes"
        params = {
            "api_key": self.emby_api_key,
            "fields": "DateCreated"
        }
        try:
            res = requests.get(url, params)
            if not res or res.status_code != 200:
                return {}
            items = res.json().get("Items") or []
            return items

        except Exception as e:
            logger.error(f"连接Users/Items出错：" + str(e))
            return {}
    
    def get_medias_count(self):
        """
        获得电影、电视剧、动漫媒体数量
        :return: MovieCount SeriesCount SongCount
        """
        if not self.emby_host or not self.emby_api_key:
            return 0
        
        url = f"{self.emby_host}/emby/Items/Counts"
        params = {
            'api_key': self.emby_api_key
        }
        try:
            res = requests.get(url, params)
            if res.status_code==200:
                result = res.json()
                return {
                    "movie": result.get("MovieCount") or 0,
                    "tv": result.get("SeriesCount") or 0,
                    "episode": result.get("EpisodeCount") or 0
                }
            else:
                logger.warning(f"Items/Counts 未获取到返回数据")
                return {
                    "movie": 0,
                    "tv": 0,
                    "episode": 0
                }
        except Exception as e:
            logger.warning(f"连接Items/Counts出错：" + str(e))
            return {
                    "movie": 0,
                    "tv": 0,
                    "episode": 0
                }
        
    def get_media_play_report(
            self,
            report_type: str,
            user_id: str="",
            days: int=30,
            ):
        """
        获取用户播放记录

        Args:
            report_type (str): MoviesReport | TvShowsReport
            user_id (str, optional): 默认获取全部用户播放记录
            days (int, optional): 默认获取最近30天内

        Returns:
            _type_: _description_
        """
        if not self.emby_host or not self.emby_api_key:
            return []
        
        url = f"{self.emby_host}/emby/user_usage_stats/{report_type}"
        params = {
            'user_id': user_id,
            'days': days,
            'api_key': self.emby_api_key
        }
        try:
            res = requests.get(url, params)
            if res:
                result = res.json()
                if result:
                    result.sort(key=lambda x:x["time"], reverse=True)
                return format_report_data(result)
            else:
                # logger.warning(f"user_usage_stats/{report_type} 未获取到返回数据")
                return []
        except Exception as e:
            # logger.warning(f"连接user_usage_stats/{report_type}出错：" + str(e))
            return []

    def get_playing_mediasoure_id(self):
        """
        获取正在播放的媒体id
        """
        url = f"{self.emby_host}/emby/Sessions"
        params = {
            'IncludeAllSessionsIfAdmin': 'true',
            'IsPlaying': 'true',
            'api_key': self.emby_api_key
        }
        try:
            res = requests.get(url, params)
            if result:=res.json():
                playing_mediasoure_id = {}
                for playing in result:
                    media_id = playing["PlayState"]["MediaSourceId"]
                    if media_id not in playing_mediasoure_id:
                        # playing_mediasoure_id[media_id] = [playing["DeviceId"]]
                        playing_mediasoure_id[media_id] = [playing["DeviceId"]]
                    else:
                        playing_mediasoure_id[media_id].append(playing["DeviceId"])
                return playing_mediasoure_id
            else:
                return {}
        except Exception as e:
            logger.warning(f"连接emby/Sessions出错：" + str(e))
            return {}

    def get_emby_playback_info(
            self, 
            video_id: str|int,
            param: dict={}, 
            data: dict={},
            is_playback:str ="true"
            ):
        """
        根据video_id从emby中获取视频信息

        Args:
            video_id (str): _description_
            is_playback (str, optional): _description_. Defaults to "true".
            param (dict, optional): _description_. Defaults to {}.
            data (dict, optional): _description_. Defaults to {}.

        Returns:
            _type_: _description_
        """
        headers = {
        "Content-Type": "application/json;charset=utf-8"
        }
        playback_info_url = f'{self.emby_host}/Items/{video_id}/PlaybackInfo'
        if param:
            param = dict(param)
        param["IsPlayback"] = is_playback
        param["api_key"] = self.emby_api_key
        try:
            int(video_id)
            param["MediaSourceId"] = f"mediasource_{video_id}"
        except:
            param["MediaSourceId"] = video_id

        try:
            resp = requests.post(playback_info_url, data=json.dumps(data), headers=headers, params=param, timeout=20)
            if resp.status_code == 200:
                playback_info = resp.json()
                for media in playback_info.get("MediaSources", []):
                    if media["Id"] != param["MediaSourceId"]:
                        temp_param = param.copy()
                        temp_param["MediaSourceId"] = media["Id"]
                        requests.post(playback_info_url, data=json.dumps(data), headers=headers, params=temp_param, timeout=20)
                return resp.json()
            else:
                logger.info(resp.text)
            return {}
        except requests.exceptions.ReadTimeout:
            logger.warning(f"获取 {video_id} 媒体数据超时")
            return {}
        except:
            logger.warning(f"获取 {video_id} 媒体数据失败")
            return {}

    def get_emby_video_id_by_sync_job(self, file_id):
        """
        根据file_id获取emby中的video_id(安卓app下载使用)

        Args:
            file_id (_type_): _description_

        Returns:
            _type_: _description_
        """
        sync_jobs_url = f'{self.emby_host}/Sync/JobItems?api_key={self.emby_api_key}'
        headers = {
        "Content-Type": "application/json;charset=utf-8",
        }
        resp = requests.get(sync_jobs_url, headers=headers)
        if resp.status_code == 200:
            for item in resp.json()["Items"]:
                if str(item["Id"])==str(file_id):
                    return item["ItemId"]
    
    def get_remote_image_by_id(self, item_id: str, image_type: str):
        """
        根据ItemId从Emby查询TMDB的图片地址
        :param item_id: 在Emby中的ID
        :param image_type: 图片的类弄地，poster或者backdrop等
        :return: 图片对应在TMDB中的URL
        """
        if not self.emby_host or not self.emby_api_key:
            return None
        url = f"{self.emby_host}/emby/Items/{item_id}/RemoteImages"
        params = {
            "api_key": self.emby_api_key
        }
        try:
            resp = requests.get(url, params=params)
            if resp:
                images = resp.json().get("Images")
                if images:
                    for image in images:
                        if image.get("ProviderName") == "TheMovieDb" and image.get("Type") == image_type:
                            return image.get("Url")
            # 数据为空
            # logger.info(f"Items/RemoteImages 未获取到返回数据")
        except Exception as e:
            logger.warning(f"连接Items/Id/RemoteImages出错：" + str(e))
        return None

    def get_primary_image_by_id(self, item_id: str):
        # 获取item的poster图url

        if not self.emby_host or not self.emby_api_key:
            return ""
        url = f"{self.emby_host}/emby/Items/{item_id}/Images/Primary?api_key={self.emby_api_key}"
        return url
    
    def upload_library_image(self, item_id: str, image_data, library_name: str):
        """上传图片到Jellyfin服务器"""
        try:
            if not self.emby_host or not self.emby_api_key:
                return None
            # 构造 URL 和请求头
            url = f"{self.emby_host}/Items/{item_id}/Images/Primary"
            headers = {
                "Content-Type": "Image/jpeg",
            }
            params = {
                "api_key": self.emby_api_key,
            }
            response = requests.post(url, headers=headers, params=params, data=image_data, timeout=30)

            if response.status_code in (200, 204):
                logger.info(
                    f"更新 {library_name} 封面图成功"
                )
            else:
                logger.error(
                    f"更新 {library_name} 封面图失败: 详细报错: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            logger.error(
                f"更新 {library_name} 封面图失败: 详细报错: {e}"
            )
                
    def get_webhook_message(self, message: dict):
        try:
            if "Item" not in message:
                return None
            
            event: str = message["Event"]
            event_message = {
                "title": "",
                "description": "",
                "picurl": ""
            }
            # logger.info(message)

            description = "剧情："+message["Description"].replace(u"\u3000\u3000", "").replace(u"\r", "") if "Description" in message else ""
            if "Overview" in message["Item"]:
                Overview = "剧情："+message["Item"]["Overview"].replace(u"\u3000\u3000", "").replace(u"\r", "") if message["Item"]["Overview"] else ""
            else:
                Overview = ""

            if len(description)>100:
                description = description[:100] + "...\n"
            elif "Tmdb" in description:
                description = f"剧集：{description.replace('剧情：', "").split('\n')[0]}\n"
                if len(Overview)>100:
                    description += Overview[:100] + "...\n"
                elif Overview:
                    description += Overview + "\n"
            else:
                description = Overview
                if description and len(description)>100:
                    description = description[:110] + "...\n"
                elif description:
                    description += "\n"
            
            media_type = message["Item"]["Type"]
            year = ""
            if 'ProductionYear' in message["Item"]:
                year += f" ({message['Item']['ProductionYear']})"
            
            if event.startswith("playback"):
                description = f"{description[:80]}...\n" if len(description)>80 else description
                try:
                    client_info = f"IP地址：{message['Session']['RemoteEndPoint']}\n客户端：{message['Session']['Client']} {message['Session']['ApplicationVersion']}\n"
                except:
                    client_info = ""
                event_message["description"] = f"{description}{client_info}时间：   {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z%z')}"
                event_message["title"] = message["Title"]
                pic_url = self.get_remote_image_by_id(message["Item"]["Id"], image_type="Backdrop")
                if not pic_url and media_type == "Episode":
                    pic_url = self.get_remote_image_by_id(message["Item"]["SeriesId"], image_type="Backdrop")
                if pic_url:
                    event_message["picurl"] = pic_url

            elif event == "library.new":
                event_message["description"] = f"{description}时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z%z')}"
                if media_type == "Series":
                    counts = re.findall(r"已添加了 ([0-9]{1,5}) 项到", message["Title"], re.S)[0]
                    event_message["title"] = f"新入库剧集 {message['Item']['Name']}{year} 共{counts}集"
                    pic_url = self.get_remote_image_by_id(message["Item"]["Id"], image_type="Backdrop")
                elif media_type == "Episode":
                    event_message["title"] = f"新入库剧集 {message['Item']['SeriesName']} S{message['Item']['ParentIndexNumber']}E{message['Item']['IndexNumber']} {message['Item']['Name']}"
                    pic_url = self.get_remote_image_by_id(message["Item"]["Id"], image_type="Primary")
                    if not pic_url:
                        pic_url = self.get_remote_image_by_id(message["Item"]["SeriesId"], image_type="Backdrop")
                elif media_type == "Movie":
                    event_message["title"] = f"新入库电影 {message['Item']['Name']}{year}"
                    pic_url = self.get_remote_image_by_id(message["Item"]["Id"], image_type="Backdrop")

                if pic_url:
                    event_message["picurl"] = pic_url

            elif event == "library.deleted":
                event_message["description"] = f"{description}时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z%z')}"
                event_message["picurl"] = "https://cdn.pixabay.com/photo/2017/07/18/23/23/folder-2517423_1280.png"
                if media_type == "Folder":
                    return None
                elif media_type in "Movie":
                    event_message["title"] = f"删除电影 {message['Item']['Name']}{year}"
                elif media_type == "Episode":
                    event_message["title"] = f"删除剧集 {message['Item']['SeriesName']} S{message['Item']['ParentIndexNumber']}E{message['Item']['IndexNumber']} {message['Item']['Name']}"
                elif media_type == "Series":
                    event_message["title"] = f"删除剧集 {message['Item']['Name']}{year}"
                elif media_type == "Season":
                    event_message["title"] = f"删除剧集 {message['Item']['SeriesName']} S{message['Item']['IndexNumber']} {message['Item']['Name']}"
                
            return event_message
        except Exception as error:
            logger.warning(f"解析emby webhook消息失败, 详细报错: {error.__str__()}")
            return None
    
    def base_html_player(self, version: str=""):
        """
        获取BaseHtmlPlayer
        """
        url = f"{self.emby_host}/web/modules/htmlvideoplayer/basehtmlplayer.js"
        params = {
            'api_key': self.emby_api_key
        }
        if version:
            params['v'] = version
        try:
            res = requests.get(url, params)
            if result:=res.text:
                return result
            else:
                return ""
        except Exception as e:
            logger.warning(f"连接web/modules/htmlvideoplayer/basehtmlplayer.js出错：" + str(e))
            return ""
        

def format_report_data(report: list[dict]):
    format_report = []
    for item in report:
        seconds = item.get("time") or 0
        hours = seconds // 3600  # 计算小时
        minutes = (seconds % 3600) // 60  # 计算分钟
        remaining_seconds = seconds % 60  # 计算剩余秒数
        format_report.append({
            "label": item.get("label") or "",
            "time": f"{hours:02}:{minutes:02}:{remaining_seconds:02}",
            "value": seconds
        })
    return format_report

def analyse_webhook_episodes(overvies: str):
    tv_shows = {}
    try:
        overvies = overvies.split("TmdbId")[0].replace("\n", "")
        for season_str in overvies.split("/"):
            season_items = season_str.strip(" ").split(" ")
            season_name = int(season_items[0][1:])
            tv_shows[season_name] = []
            for episode_str in season_items[1:]:
                episode_str = episode_str.strip(",")
                if "-" in episode_str:
                    episode_items = episode_str.split("-")
                    start = int(episode_items[0][1:])
                    end = int(episode_items[1][1:])
                    for i in range(start, end+1):
                        tv_shows[season_name].append(i)
                else:
                    tv_shows[season_name].append(int(episode_str[1:]))
    except:
        logger.warning(f"分析入库剧集失败: {traceback.format_exc()}")
        logger.info(f"Overviews: {overvies}")
    return tv_shows
