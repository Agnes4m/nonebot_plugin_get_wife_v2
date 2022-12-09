import asyncio
from random import choice
from nonebot.plugin.on import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Bot,  GroupMessageEvent ,message
from nonebot.adapters.onebot.v11.message import MessageSegment
import random
import nonebot
import os
from pathlib import Path
try:
    import ujson as json
except ModuleNotFoundError:
    import json
from .utils import *
cdTime = 3600    # 分手后需要cdTime秒才能再次开始配对
cd_dir = {}      # cd_dir存储配对的QQ号和时间戳         {qq:time}
wife_dir = {}    # wife_dir存储配对的对象               {qq:[qq,nickname1,nickname2]}
ejaculation_CD={} # 射精CD
record_waifu = {}

get_wife = on_command(
    "抽老婆", aliases={"选妃", "娶群友","男同匹配", "男同配对"}, priority=10, block=True)
break_up = on_command("分手", aliases={"离婚"}, priority=10, block=True)
fuck_group_member = on_command("日群友", aliases={"草群友","透群友"}, priority=10, block=True)

sendmessage = [
    "醒醒你没有老婆",
    "神经病，凡是美少女都想让他当你老婆吗？",
    "死肥猪好好看清楚你自己啊！",
    "死肥宅也配选老婆？",
    "喂喂喂！清醒清醒！谁要当你老婆啊",
    "死肥宅就应该孤独一生啊"
]


@break_up.handle()
async def _(event: GroupMessageEvent):
    qid = event.user_id
    global record_waifu
    if qid in wife_dir:
        reply = f"坏欸, {wife_dir[qid][1]}({qid}) 与 {wife_dir[qid][2]}({wife_dir[qid][0]})分手了"
        wife_dir.pop(qid)
        A = event.user_id
        B = int(record_waifu[event.group_id][event.user_id])
        del record_waifu[event.group_id][A]
        del record_waifu[event.group_id][B]
        await break_up.send(reply)
    else:
        await break_up.send('你都没对象你和谁分手呢?')

@get_wife.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    qid = event.user_id                    # 用户ID
    group_id = event.group_id              # 群ID
    await pretreatment(event, qid)         # 前置处理
    global record_waifu
    record_waifu.setdefault(group_id,{})  
    req_user_card = await get_user_card(bot, group_id,qid)       # 请求者的昵称

    # 获取群成员列表
    prep_list = await bot.get_group_member_list(group_id=group_id)
    prep_list = [prep.get("user_id", 114514) for prep in prep_list]
    prep_list.remove(qid)
    

    # 随机抽取幸运成员
    lucky_user = choice(prep_list)
    lucky_user_card = await get_user_card(bot, group_id, lucky_user)
    
    #写入群cp
    member_list = prep_list
    i = 0
    while i < len(member_list):
        if member_list[i]['user_id'] in record_waifu[group_id].keys():
            del member_list[i]
        else:
            i += 1
    else:
        if member_list:
            member_list.sort(key = lambda x:x["last_sent_time"] ,reverse = True)
            user_id = req_user_card
            member = lucky_user
            record_waifu[group_id].update(
                {
                    user_id: member['user_id'],
                    member['user_id']: user_id
                    }
                )
    
    # sleep三秒
    repo_0 = f"现在咱将随机抽取一位幸运裙友\n成为{req_user_card}的老婆！"
    await get_wife.send(repo_0)
    await asyncio.sleep(3)

    # 构造消息
    url = f"http://q1.qlogo.cn/g?b=qq&nk={lucky_user}&s=640"
    repo_1 = f"好欸！{lucky_user_card}({lucky_user}) \n"
    repo_2 = f" 成为了 {req_user_card}({qid}) 的老婆" 
    
    
    wife_dir.update({qid: [lucky_user, req_user_card, lucky_user_card]})
    cd_dir.update({qid: event.time})
    await get_wife.finish(repo_1 + MessageSegment.image(url) + repo_2)


@fuck_group_member.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    qid = event.user_id                    # 用户ID
    group_id = event.group_id              # 群ID
    # CD处理
    try:
        cd = event.time - ejaculation_CD[qid]
    except KeyError:
        cd = cdTime + 1
    if cd > cdTime or event.get_user_id() in nonebot.get_driver().config.superusers:
        ejaculation_CD.update({qid: event.time})
        req_user_card = await get_user_card(bot, group_id,qid)       # 请求者的昵称 
        # 获取群成员列表
        prep_list = await bot.get_group_member_list(group_id=group_id)
        prep_list = [prep.get("user_id", 114514) for prep in prep_list]
        prep_list.remove(qid)

        # 随机抽取幸运成员
        lucky_user = choice(prep_list)
        lucky_user_card = await get_user_card(bot, group_id, lucky_user)
        repo_0 = f"现在咱将随机抽取一位幸运裙友\n送给{req_user_card}色色！"
        await fuck_group_member.send(repo_0)

        # 休眠
        fuckingTime = random.randint(1,20)
        await asyncio.sleep(fuckingTime)
        # 容量
        capacity = random.uniform(1,100)

        # 构造消息
        url = f"http://q1.qlogo.cn/g?b=qq&nk={lucky_user}&s=640"
        repo_1 = f"好欸！{req_user_card}({qid})用时{fuckingTime}秒 \n给 {lucky_user_card}({lucky_user}) 注入了{round(capacity,3)}毫升的脱氧核糖核酸" 
        await fuck_group_member.send(repo_1 + MessageSegment.image(url))

    else:
        await fuck_group_member.finish(f"你已经榨不出来任何东西了\nCD剩余时间：{round(cdTime - cd,3)}s")





async def get_user_card(bot: Bot, group_id, qid):
    # 返还用户nickname
    user_info: dict = await bot.get_group_member_info(group_id=group_id, user_id=qid)
    user_card = user_info["card"]
    if not user_card:
        user_card = user_info["nickname"]
    return user_card


async def pretreatment(event: GroupMessageEvent, qid: int):
    # 如果有对象了的话，就不能再次配对
    if qid in wife_dir:
        url = f"http://q1.qlogo.cn/g?b=qq&nk={wife_dir[qid][0]}&s=640"
        head_portrait = MessageSegment.image(url)
        await get_wife.finish(f"你当前亲爱的是{wife_dir[qid][2]}({wife_dir[qid][0]})"+head_portrait+"进行新的配对需要先分手", at_sender=True)
    await CD_check(event, qid)
    voice_path = Path(os.path.join(os.path.dirname(__file__), "resource"))
    all_file_name = os.listdir(str(voice_path))
    voicefile = random.choice(all_file_name)
    # random一下准备挨骂吧!
    if(random.random() < 0.3):
        await get_wife.finish(message=f"{random.choice(sendmessage)}"+MessageSegment.image(Path(os.path.join(os.path.dirname(__file__), "resource")) / voicefile))



async def CD_check(event: GroupMessageEvent, qid: int):
    # cd处理部分
    try:
        cd = event.time - cd_dir[qid]
    except KeyError:
        cd = cdTime + 1
    if cd < cdTime:
        time_last = cdTime - cd
        hours, minutes, seconds = 0, 0, 0
        if time_last >= 60:
            minutes, seconds = divmod(time_last, 60)
            hours, minutes = divmod(minutes, 60)
        else:
            seconds = time_last
        cd_msg = f"{str(hours) + '小时' if hours else ''}{str(minutes) + '分钟' if minutes else ''}{str(seconds) + '秒' if seconds else ''}"
        await get_wife.finish(f"臭东西！你换对象的CD还有{cd_msg}", at_sender=True)
        
# 查看娶群友卡池

waifu_list = on_command("查看群友卡池", aliases = {"群友卡池"}, priority = 90, block = True)

@waifu_list.handle()
async def _(bot:Bot, event: GroupMessageEvent):
    member_list = await bot.get_group_member_list(group_id = event.group_id)
    i = 0
    while i < len(member_list):
        if member_list[i]['user_id'] in record_waifu.setdefault(event.group_id,{}).keys():
            del member_list[i]
        else:
            i += 1
    else:
        if member_list:
            member_list.sort(key = lambda x:x["last_sent_time"] ,reverse = True)
            msg ="卡池：\n——————————————\n"
            for member in member_list[:80]:
                nickname = member['card'] or member['nickname']
                msg += f"{nickname}\n"
            else:
                output = text_to_png(msg[:-1])
                await waifu_list.finish(MessageSegment.image(output))
        else:
            await waifu_list.finish("群友已经被娶光了。")


# 查看本群CP

cp_list = on_command("本群CP", aliases = {"本群cp"}, priority = 90, block = True)

@cp_list.handle()
async def _(bot:Bot, event: GroupMessageEvent):
    group_id = event.group_id
    global record_waifu
    record_waifu.setdefault(group_id,{})
    lst = record_waifu[group_id].keys()
    if lst:
        listA = []
        listB = []
        for A in lst:
            listA.append(A)
            B = record_waifu[group_id][A]
            if B not in listA and B != A:
                listB.append(B)

        msg = ""
        for user_id in listB:
            try:
                member = await bot.get_group_member_info(group_id = group_id, user_id = record_waifu[group_id][user_id])
                niknameA = member['card'] or member['nickname']
            except:
                niknameA = ""
            try:
                member = await bot.get_group_member_info(group_id = group_id, user_id = user_id)
                niknameB = member['card'] or member['nickname']
            except:
                niknameB = ""
            msg += f"♥ {niknameA} | {niknameB}\n"
        if msg:
            output = text_to_png("本群CP：\n——————————————\n" + msg[:-1])
            await cp_list.finish(MessageSegment.image(output))

    await cp_list.finish("本群暂无cp哦~")