import re
from datetime import timedelta, datetime
from typing import Any, Optional, List, Dict, Callable

from attr import define
from telegram import Update

from .actions import Action, Reply, TextReplyContent
from .clock import Clock
from .history import History
from .slowmode_user_repository import SlowmodeUserRepository
from .types import HandlerFunc


def get_user_id_handler(hist: History) -> HandlerFunc:
    def _handle(update: Update, context: Any) -> Optional[Action]:
        username = update.message.text.split(" ", maxsplit=1)[1].strip().lstrip("@")
        user_id = hist.get_user_id(username)
        if user_id:
            if len(user_id) == 1:
                user_id = user_id[0]
                return Reply(update.message, TextReplyContent(str(user_id)))
            else:
                return Reply(update.message, TextReplyContent(f"there are many ids matching username {username}"))
        return Reply(update.message, TextReplyContent(f"user id for username {username} not found"))
    return _handle


@define
class SlowCommandHandler:
    repository: SlowmodeUserRepository
    hist: History
    clock: Clock

    def __call__(self, update: Update, context: Any) -> Optional[Action]:
        return self.handle(update, context)

    def handle(self, update: Update, context: Any) -> Optional[Action]:
        command_args = update.message.text.split(" ")[1:]
        subcommand = command_args[0]
        parsed_args = self._parse_args(command_args[1:])
        print(f"parsed args for slow command: {parsed_args}")
        username = self.hist.get_user_name(parsed_args.user_id)
        match subcommand:
            case "create":
                print("creating restriction")
                self.repository.create_restriction(
                    chat_id=parsed_args.chat_id,
                    user_id=parsed_args.user_id,
                    interval=parsed_args.interval,
                    until_date=parsed_args.until_date
                )
                print("restriction created")
                reply_content = TextReplyContent(
                    _format_restriction(
                        parsed_args.user_id,
                        username,
                        parsed_args.interval,
                        parsed_args.until_date)
                )
                return Reply(update.message, reply_content)
            case "get":
                restriction = self.repository.get_active_restriction(
                    chat_id=parsed_args.chat_id,
                    user_id=parsed_args.user_id
                )
                if restriction:
                    reply_text = _format_restriction(
                        parsed_args.user_id,
                        username,
                        restriction.interval,
                        restriction.until_date
                    )
                else:
                    reply_text = f"user @{username} is not slowed"
                return Reply(update.message, TextReplyContent(reply_text))
            case "update":
                restriction = self.repository.update_restriction(
                    chat_id=parsed_args.chat_id,
                    user_id=parsed_args.user_id,
                    interval=parsed_args.interval
                )
                reply_text = _format_restriction(
                    parsed_args.user_id,
                    username,
                    restriction.interval,
                    restriction.until_date
                )
                return Reply(update.message, TextReplyContent(reply_text))
            case "delete":
                self.repository.delete_restriction(
                    chat_id=parsed_args.chat_id,
                    user_id=parsed_args.user_id
                )
                return Reply(update.message, TextReplyContent(f"user @{username} is not restricted anymore"))

    def _parse_args(self, args: List[str]) -> "SlowCommandArgs":
        args_dict = {pair[0]: pair[1] for pair in map(lambda arg: arg.split("="), args)}
        _update_dict_entry(args_dict, "interval", self._parse_interval)
        _update_dict_entry(args_dict, "until_date", self._parse_datetime)
        return SlowCommandArgs(**args_dict)

    def _parse_interval(self, arg: str) -> timedelta:
        match = re.match(_INTERVAL_PATTERN, arg)
        match matched_unit := match.group("unit"):
            case "s":
                unit = "seconds"
            case "m":
                unit = "minutes"
            case "h":
                unit = "hours"
            case "d":
                unit = "days"
            case _:
                raise Exception(f"Unknown interval unit: {matched_unit}")
        amount = int(match.group("amount"))
        return timedelta(**{unit: amount})

    def _parse_datetime(self, arg: str) -> datetime:
        duration = self._parse_interval(arg)
        return self.clock.now() + duration


def _format_restriction(user_id: int, username: Optional[str], interval: timedelta, until_date: datetime) -> str:
    if username:
        user_info = f"@{username} (id: {user_id})"
    else:
        user_info = str(user_id)
    return f"user {user_info} is slowed with interval {interval} until {until_date}"


@define
class SlowCommandArgs:
    chat_id: int
    user_id: int
    interval: Optional[timedelta]
    until_date: Optional[datetime]


_INTERVAL_PATTERN = re.compile(r"(?P<amount>[1-9][0-9]*)(?P<unit>\w+)", re.IGNORECASE | re.UNICODE)


def _update_dict_entry(dictionary: Dict[str, Any], key: str, mapper: Callable[[Any], Any]) -> None:
    if key in dictionary:
        dictionary[key] = mapper(dictionary[key])
