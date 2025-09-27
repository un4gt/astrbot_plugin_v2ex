from httpx import AsyncClient
from typing import Dict, List, Optional, Any
from astrbot.api import logger
import httpx
import datetime


class V2exAPI:
    """V2EX API 客户端"""

    def __init__(self, personal_access_token: str):
        self.token = personal_access_token
        self.v2_base_url = "https://www.v2ex.com/api/v2"

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            "Authorization": f"Bearer {self.token}",
        }

    async def get_notifications(self, page: int = 1) -> Optional[Dict[str, Any]]:
        """获取通知列表

        Args:
            page: 页码，默认为1（只获取第一页）

        Returns:
            通知数据字典，失败返回None
        """
        if not self.token:
            logger.error("未配置 Personal Access Token")
            return None

        url = f"{self.v2_base_url}/notifications"
        params = {"p": page}

        try:
            async with AsyncClient(headers=self._get_headers()) as client:
                response = await client.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"成功获取通知列表，页码: {page}")
                    return data
                elif response.status_code == 401:
                    logger.error("Personal Access Token 无效或已过期")
                    return None
                else:
                    logger.error(f"获取通知列表失败，HTTP状态码: {response.status_code}")
                    return None
        except httpx.RequestError as e:
            logger.error(f"网络请求失败: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"获取通知列表时发生错误: {str(e)}")
            return None

    async def get_profile(self) -> Optional[Dict[str, Any]]:
        """获取当前用户的个人信息

        Returns:
            用户信息字典，失败返回None
        """
        if not self.token:
            logger.error("未配置 Personal Access Token")
            return None

        url = f"{self.v2_base_url}/member"

        try:
            async with AsyncClient(headers=self._get_headers()) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    logger.info("成功获取个人信息: %s", data)
                    return data
                elif response.status_code == 401:
                    logger.error("Personal Access Token 无效或已过期")
                    return None
                else:
                    logger.error(
                        f"获取个人信息失败，HTTP状态码: {response.status_code}"
                    )
                    return None
        except httpx.RequestError as e:
            logger.error(f"网络请求失败: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"获取个人信息时发生错误: {str(e)}")
            return None

    def format_notification(self, notification: Dict[str, Any]) -> str:
        """格式化单个通知为可读文本

        Args:
            notification: 通知数据

        Returns:
            格式化后的通知文本
        """
        try:
            if not notification['success']:
                return ''

            notifications = notification['result']
            all_notifications = ''
            temp_str = 'text: {0}\n\npayload: {1}\n\n created_at: {2}'
            for no in notifications:
                dt = datetime.datetime.fromtimestamp(no['created'])
                all_notifications += temp_str.format(no['text'], no['payload'], dt.strftime('%Y-%m-%d %H:%M:%S'))

            return all_notifications
        except Exception as e:
            logger.error(f"格式化通知时发生错误: {str(e)}")
            return f"通知内容解析失败: {str(notification)}"

    def format_profile(self, profile: Dict[str, Any]) -> str:
        """格式化用户信息为可读文本

        Args:
            profile: 用户信息

        Returns:
            格式化后的用户信息文本
        """
        try:
            if not profile['success']:
                return ''
            profile = profile['result']
            username = profile.get("username", "未知")
            bio = profile.get("bio", "无")
            location = profile.get("location", "未知")
            website = profile.get("website", "无")
            created = profile.get("created", 0)

            # 格式化注册时间
            import datetime

            try:
                dt = datetime.datetime.fromtimestamp(created)
                created_str = dt.strftime("%Y-%m-%d")
            except:
                created_str = "未知"

            profile_text = f"""👤 用户信息
用户名: {username}
个人简介: {bio}
地区: {location}
个人网站: {website}
注册时间: {created_str}"""

            return profile_text
        except Exception as e:
            logger.error(f"格式化用户信息时发生错误: {str(e)}")
            return f"用户信息解析失败: {str(profile)}"
