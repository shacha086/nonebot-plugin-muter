import asyncio
import random
from asyncio import Task

from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot

from .classes import User, Role
from .data_source import MAX_COUNT, EXPIRE_TIME
from .utils import extract_member_at, get_user_info, get_member_name, mute_member, get_member_mute_time_seconds

matcher = on_command("/举办")

is_voting: bool = False
count: int = 0
current_user: User
voted_members: set = set()
task: Task


async def initialize():
    global is_voting, count, current_user, voted_members
    is_voting = False
    count = 0
    current_user = None
    voted_members = set()


def add_count():
    global count
    count += 1


async def start_vote(bot: Bot, event: GroupMessageEvent, member_at: User):
    global is_voting, current_user, task
    is_voting = True
    current_user = member_at

    async def _task():
        await asyncio.sleep(EXPIRE_TIME)
        await bot.send_group_msg(
            group_id=event.group_id,
            message="上一个举办已超时。"
        )
        await initialize()

    task = asyncio.create_task(_task(), name='expire')
    await matcher.finish(f"举办已开始，发送\"投\"来给{get_member_name(member_at)}投票。")


@matcher.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    global is_voting

    role = (await get_user_info(bot, event.group_id, int(bot.self_id))).role
    if role == Role.MEMBER:
        await matcher.finish("我至少需要一个绿帽来禁言吧？")

    if is_voting:
        await matcher.finish("有一个正在进行的举办，请稍后再试")

    if (member_at := extract_member_at(event.message)) == -1:
        await matcher.finish("你要举办谁？")

    member_at = await get_user_info(bot, event.group_id, member_at)

    if role == Role.ADMIN:
        if member_at.role != Role.MEMBER:
            await matcher.finish("对面权限太高，禁不掉啦！")

    await start_vote(bot, event, member_at)


matcher = on_command("投")


@matcher.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    global is_voting
    if not is_voting:
        await matcher.finish("没有正在进行的举办🤔")

    if str(event.user_id) not in bot.config.superusers:
        if event.user_id in voted_members:
            await matcher.finish("你已经投过票了，，")

    add_count()
    voted_members.add(event.user_id)
    if count == MAX_COUNT:
        duration = random.randint(10, 20)
        _ = duration * 60 + await get_member_mute_time_seconds(
                bot,
                event.group_id,
                current_user
            )
        await mute_member(
            bot,
            event.group_id,
            current_user,
            _ if _ <= 2592000 else 2591999
        )
        await matcher.send(f"🎉陶片禁言成功！{get_member_name(current_user)}被禁言了{duration}分钟！🥳🍾")
        task.cancel()
        await initialize()
        return
    else:
        await matcher.finish(f"已经给{get_member_name(current_user)}投了一票！({count}/5)")
