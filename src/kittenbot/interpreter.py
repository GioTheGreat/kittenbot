from attr import define
from telegram import Bot

from .actions import Action, Reply, DocumentReplyContent, TextReplyContent


@define
class Interpreter:
    bot: Bot

    async def run_action(self, action: Action) -> None:
        match action:
            case Reply(reply_to_message, content):
                match content:
                    case DocumentReplyContent(filename, document):
                        await self.bot.send_document(
                            reply_to_message.chat_id,
                            document=document,
                            filename=filename,
                            reply_to_message_id=reply_to_message.id)
                    case TextReplyContent(text):
                        await self.bot.send_message(
                            reply_to_message.chat_id,
                            text=text,
                            reply_to_message_id=reply_to_message.id)
