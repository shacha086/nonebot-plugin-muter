import datetime

from nonebot.adapters.onebot.v11 import Bot

from . import User


def extract_member_at(message):
    for segment in message:
        if (segment.type == "at") and ("qq" in segment.data):
            return segment.data["qq"]

    return -1


def get_member_name(member: User):
    return member.card if not len(member.card) == 0 else member.nickname


async def get_user_info(bot: Bot, group_id: int, user_id: int) -> User:
    temp = await bot.get_group_member_info(group_id=group_id, user_id=user_id)
    return User(**temp)


async def mute_member(bot: Bot, group_id: int, member: User, duration: int):
    await bot.set_group_ban(group_id=group_id, user_id=member.user_id, duration=duration)


async def get_member_mute_time_seconds(bot: Bot, group_id: int, member: User) -> int:
    member_list = await bot.get_group_member_list(group_id=group_id, no_cache=True)
    mute_end_timestamp = -1
    for _ in member_list:
        if _['user_id'] == member.user_id:
            mute_end_timestamp = _['shut_up_timestamp']
            break
    if mute_end_timestamp <= datetime.datetime.now().timestamp():
        return 0
    _ = (mute_end_timestamp - datetime.datetime.now().timestamp())
    return _
