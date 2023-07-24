from attr import define
from telegram import Bot, ChatPermissions

from .actions import Action, Reply, DocumentReplyContent, TextReplyContent, RestrictMember, CompositeAction


@define
class Interpreter:
    bot: Bot

    async def run_action(self, action: Action) -> None:
        print(f"running action {action}")
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
            case RestrictMember(chat_id, user_id, until_date):
                await self.bot.restrict_chat_member(
                    chat_id,
                    user_id,
                    ChatPermissions.no_permissions(),
                    until_date)
            case CompositeAction(parts):
                for part in parts:
                    await self.run_action(part)
            case _:
                raise Exception(f"Unknown action: {action}")
