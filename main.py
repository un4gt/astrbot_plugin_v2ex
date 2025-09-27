from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.core.config.astrbot_config import AstrBotConfig
from .v2ex_api import V2exAPI


@register("astrbot_plugin_v2ex", "un4gt", "通过 astrbot 浏览 v2ex 网站", "1.0.2")
class V2ex(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self._personal_access_token = config.get("personal_access_token")
        self.api_client = None

    async def initialize(self):
        if (
            self._personal_access_token is None
            or self._personal_access_token.strip() == ""
        ):
            logger.error(
                "未配置个人访问令牌，请在配置文件中添加 personal_access_token 字段"
            )
            return

        self.api_client = V2exAPI(self._personal_access_token)
        logger.info("V2EX 插件初始化成功")

    @filter.command_group("v2ex")
    def v2ex(self):
        """V2EX 相关命令"""
        pass

    @v2ex.command("notifications")
    async def notifications(self, event: AstrMessageEvent, page: int = 1):
        """获取通知列表（默认第一页）

        Args:
            page: 页码，默认为1
        """
        if not self.api_client:
            yield event.plain_result(
                "插件未正确初始化，请检查配置中的 personal_access_token"
            )
            return

        try:
            # 只获取第一页
            notifications_data = await self.api_client.get_notifications(page=1)

            if notifications_data is None:
                yield event.plain_result(
                    "获取通知失败，请检查网络连接或Personal Access Token是否有效"
                )
                return

            # 检查是否为列表格式
            if isinstance(notifications_data, list):
                notifications = notifications_data
            else:
                # 如果是包含result字段的对象
                notifications = notifications_data.get("result", [])

            if not notifications:
                yield event.plain_result("📭 暂无新通知")
                return

            # 格式化通知内容
            result_text = "📬 最新通知列表:\n\n"
            for i, notification in enumerate(notifications[:10], 1):  # 最多显示10条
                formatted_notification = self.api_client.format_notification(
                    notification
                )
                result_text += f"{i}. {formatted_notification}\n\n"

            if len(notifications) > 10:
                result_text += f"... 还有 {len(notifications) - 10} 条通知"

            yield event.plain_result(result_text)

        except Exception as e:
            logger.error(f"处理通知命令时发生错误: {str(e)}")
            yield event.plain_result(f"获取通知时发生错误: {str(e)}")

    @v2ex.command("profile")
    async def profile(self, event: AstrMessageEvent):
        """查看自己的个人信息"""
        if not self.api_client:
            yield event.plain_result(
                "插件未正确初始化，请检查配置中的 personal_access_token"
            )
            return

        try:
            profile_data = await self.api_client.get_profile()

            if profile_data is None:
                yield event.plain_result(
                    "获取个人信息失败，请检查网络连接或Personal Access Token是否有效"
                )
                return

            # 格式化个人信息
            formatted_profile = self.api_client.format_profile(profile_data)
            yield event.plain_result(formatted_profile)

        except Exception as e:
            logger.error(f"处理个人信息命令时发生错误: {str(e)}")
            yield event.plain_result(f"获取个人信息时发生错误: {str(e)}")

    @v2ex.group("nodes")
    def nodes(self):
        """节点相关命令"""
        pass


    async def terminate(self):
        """插件卸载时的清理工作"""
        logger.info("V2EX 插件已卸载")
