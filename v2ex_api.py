from httpx import AsyncClient
from typing import Dict, List, Optional, Any
from astrbot.api import logger
import httpx


class V2exAPI:
    """V2EX API 客户端"""

    def __init__(self, personal_access_token: str):
        self.token = personal_access_token
        self.base_url = "https://www.v2ex.com/api/v2"
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
                    data = await response.json()
                    logger.info(f"成功获取通知列表，页码: {page}")
                    return data
                elif response.status_code == 401:
                    logger.error("Personal Access Token 无效或已过期")
                    return None
                else:
                    logger.error(f"获取通知列表失败，HTTP状态码: {response.status}")
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
                    data = await response.json()
                    logger.info("成功获取个人信息")
                    return data
                elif response.status_code == 401:
                    logger.error("Personal Access Token 无效或已过期")
                    return None
                else:
                    logger.error(f"获取个人信息失败，HTTP状态码: {response.status_code}")
                    return None
        except httpx.RequestError as e:
            logger.error(f"网络请求失败: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"获取个人信息时发生错误: {str(e)}")
            return None

    async def get_nodes_list(self) -> Optional[List[Dict[str, Any]]]:
        """获取所有节点列表

        Returns:
            节点列表，失败返回None
        """
        # 使用旧版API获取所有节点
        url = f"{self.base_url}/nodes/all.json"

        try:
            async with AsyncClient() as client:
                response = await client.get(url)
                if response.status_code == 200:
                    data = await response.json()
                    logger.info(f"成功获取节点列表，共 {len(data)} 个节点")
                    return data
                else:
                    logger.error(f"获取节点列表失败，HTTP状态码: {response.status_code}")
                    return None
        except httpx.RequestError as e:
            logger.error(f"网络请求失败: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"获取节点列表时发生错误: {str(e)}")
            return None

    def format_notification(self, notification: Dict[str, Any]) -> str:
        """格式化单个通知为可读文本

        Args:
            notification: 通知数据

        Returns:
            格式化后的通知文本
        """
        try:
            # 根据V2EX API文档格式化通知内容
            notification_type = notification.get("type", "unknown")
            content = notification.get("content", "")
            created_at = notification.get("created_at", 0)

            # 格式化时间
            import datetime

            try:
                dt = datetime.datetime.fromtimestamp(created_at)
                time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                time_str = "未知时间"

            return f"[{notification_type}] {content}\n时间: {time_str}"
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

    def format_nodes_list(
        self, nodes: List[Dict[str, Any]], page: int = 1, page_size: int = 20
    ) -> str:
        """格式化节点列表为可读文本（分页显示）

        Args:
            nodes: 节点列表
            page: 页码
            page_size: 每页显示的节点数量

        Returns:
            格式化后的节点列表文本
        """
        try:
            if not nodes:
                return "暂无节点信息"

            # 分页处理
            total = len(nodes)
            total_pages = (total + page_size - 1) // page_size
            start_idx = (page - 1) * page_size
            end_idx = min(start_idx + page_size, total)

            if start_idx >= total:
                return f"页码超出范围，共 {total_pages} 页"

            page_nodes = nodes[start_idx:end_idx]

            nodes_text = (
                f"📋 V2EX 节点列表 (第 {page}/{total_pages} 页，共 {total} 个节点)\n\n"
            )

            for node in page_nodes:
                name = node.get("name", "未知")
                title = node.get("title", "未知")
                topics = node.get("topics", 0)

                nodes_text += f"• {title} ({name})\n  话题数: {topics}\n\n"

            if total_pages > 1:
                nodes_text += f"使用 /v2ex nodes list {page + 1} 查看下一页"

            return nodes_text
        except Exception as e:
            logger.error(f"格式化节点列表时发生错误: {str(e)}")
            return f"节点列表解析失败"
