from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.core.config.astrbot_config import AstrBotConfig

@register("astrbot_plugin_v2ex", "un4gt", "通过 astrbot 浏览 v2ex 网站", "1.0.0")
class V2ex(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self._personal_access_token = config.get("personal_access_token")

    async def initialize(self):
        if self._personal_access_token is None:
            logger.error("未配置个人访问令牌，请在配置文件中添加 personal_access_token 字段")


    @filter.command("v2ex")
    async def helloworld(self, event: AstrMessageEvent):
        """这是一个 hello world 指令""" # 这是 handler 的描述，将会被解析方便用户了解插件内容。建议填写。
        user_name = event.get_sender_name()
        message_str = event.message_str # 用户发的纯文本消息字符串
        message_chain = event.get_messages() # 用户所发的消息的消息链 # from astrbot.api.message_components import *
        logger.info(message_chain)
        yield event.plain_result(f"Hello, {user_name}, 你发了 {message_str}!") # 发送一条纯文本消息
