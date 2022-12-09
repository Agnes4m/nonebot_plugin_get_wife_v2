from nonebot import require
from nonebot.plugin.on import on_command
from nonebot.adapters.onebot.v11 import (
    GROUP,
    Bot,
    GroupMessageEvent,
    Message,
    MessageSegment,
    )
from nonebot.adapters.onebot.v11.message import MessageSegment, Message
import nonebot
import os
import random
import asyncio
import time

try:
    import ujson as json
except ModuleNotFoundError:
    import json

from .utils import *
from .config import Config

ejaculation_CD={} # 射精CD
# 加载全局配置[]
global_config = nonebot.get_driver().config
config = Config.parse_obj(global_config.dict())

scheduler = require("nonebot_plugin_apscheduler").scheduler

# 娶群友

record_waifu = {}

waifu = on_command("抽老婆",aliases={"娶群友","选妃", "男同匹配","男同配对"},permission=GROUP,priority = 10,block = True)

no_waifu = [
    "醒醒你没有老婆",
    "神经病，凡是美少女都想让他当你老婆吗？",
    "死肥猪好好看清楚你自己啊！",
    "死肥宅也配选老婆？",
    "喂喂喂！清醒清醒！谁要当你老婆啊",
    "死肥宅就应该孤独一生啊"
    ]
happy_end= [
    "好耶~",
    "需要咱主持婚礼吗qwq",
    "不许秀恩爱！",
    "(响起婚礼进行曲♪)",
    "祝你们生八个。"
    ]

@waifu.handle()
async def _(bot:Bot, event: GroupMessageEvent):
    group_id = event.group_id
    user_id = event.user_id
    global record_waifu
    record_waifu.setdefault(group_id,{})
    req_user_info: dict = await bot.get_group_member_info(
        group_id=group_id, user_id=int(user_id)
    )
    req_user_card = req_user_info["card"]
    #判断性别来抽老婆或者老公
    if not req_user_card:
        req_user_card = req_user_info["nickname"]
    req_user_sex = req_user_info["sex"]
    is_nick = "老婆" if req_user_sex == "male" else "老公"
    at = get_message_at(event.json())
    if at and at[0] != user_id:
        at = at[0]
        if record_waifu[group_id].get(user_id,0) == 0:
            X = random.randint(1,6)
            if record_waifu[group_id].get(at,0) in (0, at):
                if X > 3:
                    if X == 6:
                        record_waifu[group_id].update(
                            {
                                user_id: at,
                                at: user_id
                                }
                            )
                        await waifu.send("恭喜你娶到了群友" + MessageSegment.at(at), at_sender=True)
                        await asyncio.sleep(1)
                    else:
                        record_waifu[group_id][user_id] = user_id
                else:
                    pass
            else:
                try:
                    member = await bot.get_group_member_info(group_id = group_id, user_id = record_waifu[group_id][at])
                except:
                    member = None
                if member:
                    if X == 6: # 彩蛋
                        await waifu.send(
                            "人家已经名花有主了~" + 
                            MessageSegment.image(file = await user_img(record_waifu[group_id][at])) +
                            "ta的CP：" + ( member['card'] or member['nickname'] ) + '\n'
                            "但是...",
                            at_sender=True
                            )
                        record_waifu[group_id].pop(record_waifu[group_id][at])
                        record_waifu[group_id].update(
                            {
                                user_id: at,
                                at: user_id
                                }
                            )
                    else:
                        await waifu.send(
                            "人家已经名花有主啦！" + 
                            MessageSegment.image(file = await user_img(record_waifu[group_id][at])) +
                            "ta的CP：" + ( member['card'] or member['nickname'] ),
                            at_sender=True
                            )
                else:
                    record_waifu[group_id].pop(record_waifu[group_id][at])
                    record_waifu[group_id].update(
                        {
                            user_id: at,
                            at: user_id
                            }
                        )
                    await waifu.send("恭喜你娶到了群友" + MessageSegment.at(at), at_sender=True)
                await asyncio.sleep(1)
        elif record_waifu[group_id][user_id] == at:
            await waifu.finish(
                "这是你的CP！"+ MessageSegment.at(record_waifu[group_id][user_id]) + '\n' +
                random.choice(happy_end) +
                MessageSegment.image(file = await user_img(record_waifu[group_id][user_id])),
                at_sender=True
                )
        elif record_waifu[group_id][user_id] == user_id:
            pass
        else:
            try:
                member = await bot.get_group_member_info(group_id = group_id, user_id = record_waifu[group_id][user_id])
            except:
                member = None
            if member:
                await waifu.finish(
                    "你已经有CP了，不许花心哦~" +
                    MessageSegment.image(file = await user_img(record_waifu[group_id][user_id])) +
                    "你的CP：" + ( member['card'] or member['nickname'] ),
                    at_sender=True
                    )
            else:
                record_waifu[group_id][user_id] = user_id
    if record_waifu[group_id].get(user_id,0) == 0:
        member_list = await bot.get_group_member_list(group_id = event.group_id)
        i = 0
        while i < len(member_list):
            if member_list[i]['user_id'] in record_waifu[group_id].keys():
                del member_list[i]
            else:
                i += 1
        else:
            if member_list:
                member_list.sort(key = lambda x:x["last_sent_time"] ,reverse = True)
                member = random.choice(member_list[:80])
                record_waifu[group_id].update(
                    {
                        user_id: member['user_id'],
                        member['user_id']: user_id
                        }
                    )
                nickname = member['card'] or member['nickname']
                membe = await bot.get_group_member_info(group_id = group_id, user_id = user_id)
                A = membe['card'] or membe['nickname']
                if record_waifu[group_id][user_id] == user_id:
                    await waifu.finish(random.choice(no_waifu), at_sender=True)
                else:
                    await waifu.send(f"现在咱将随机抽取一位幸运裙友\n成为{A}的{is_nick}！")
                    await asyncio.sleep(3)
                    await waifu.send(
                        (
                            f"好欸！{nickname} \n",
                            MessageSegment.image(file = await user_img(record_waifu[group_id][user_id])),
                            f"成为了{A}的{is_nick}！"
                            ),                            
                            )
            else:
                record_waifu[group_id][user_id] = 1
                await waifu.finish("群友已经被娶光了、\n" + random.choice(no_waifu), at_sender=True)
    else:
        if record_waifu[group_id][user_id] == event.user_id:
            await waifu.finish(random.choice(no_waifu), at_sender=True)
        elif record_waifu[group_id][user_id] == 1:
            await waifu.finish("群友已经被娶光了、\n" + random.choice(no_waifu), at_sender=True)
        else:
            try:
                member = await bot.get_group_member_info(group_id = group_id, user_id = record_waifu[group_id][user_id])
            except:
                member = None
            if member:
                nickname = member['card'] or member['nickname']
                membe = await bot.get_group_member_info(group_id = group_id, user_id = user_id)
                A = membe['card'] or membe['nickname']
                await waifu.send(f"现在咱将随机抽取一位幸运裙友\n成为{A}的{is_nick}！")
                await asyncio.sleep(3)
                await waifu.send(
                        (
                            f"好欸！{nickname} \n",
                            MessageSegment.image(file = await user_img(record_waifu[group_id][user_id])),
                            f"成为了{A}的{is_nick}！"
                            ),  
                )                          

            else:
                await waifu.finish(random.choice(no_waifu), at_sender=True)

# 分手

async def FACTOR(bot: Bot, event: GroupMessageEvent) -> bool:
    global record_waifu
    record_waifu.setdefault(event.group_id,{})
    return record_waifu[event.group_id].get(event.user_id,0) not in (0, 1, event.user_id) and config.waifu_cd_bye != -1

global cd_bye
cd_bye = {}

bye = on_command("离婚", aliases = {"分手"}, permission = FACTOR, priority = 90, block = True)

@bye.handle()
async def _(bot:Bot, event: GroupMessageEvent):
    global record_waifu, cd_bye
    cd_bye.setdefault(event.group_id,{})
    flag = cd_bye[event.group_id].setdefault(event.user_id,[0,0])
    Now = time.time()
    cd = flag[0] - Now
    if cd <= 0:
        cd_bye[event.group_id][event.user_id][0] = Now + config.waifu_cd_bye
        A = event.user_id
        print(A)
        B = int(record_waifu[event.group_id][event.user_id])
        del record_waifu[event.group_id][A]
        del record_waifu[event.group_id][B]
        await bye.finish((f"坏欸, {A} 与 {B}分手了"))
    else:
        flag[1] += 1
        if flag[1] == 1:
            await bye.finish(f"你的cd还有{round(cd/60,1)}分钟。", at_sender=True)
        elif flag[1] <= 3:
            await bye.finish(f"你已经问过了哦~ 你的cd还有{round(cd/60,1)}分钟。", at_sender=True)
        elif flag[1] <= 10:
            t = random.randint(flag[1], 3 * flag[1])
            flag[0] += t * 60
            await bye.finish(f"还问！罚时！你的cd还有{round(cd/60,1)}+{t}分钟。", at_sender=True)
        else:
            if random.randint(1,6) == 6:
                await bye.finish("哼！")

# 查看娶群友卡池

waifu_list = on_command("查看群友卡池", aliases = {"群友卡池"}, permission = GROUP, priority = 90, block = True)

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

cp_list = on_command("本群CP", aliases = {"本群cp"}, permission=GROUP, priority = 90, block = True)

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


# 透群友

record_yinpa = {}

yinpa = on_command("透群友",aliases={"草群友","日群友"}, permission=GROUP, priority = 10, block = True)

@yinpa.handle()
async def _(bot:Bot, event: GroupMessageEvent):
    group_id = event.group_id
    user_id = event.user_id
    member_list = await bot.get_group_member_list(group_id = event.group_id)
    member_list.sort(key = lambda x:x["last_sent_time"] ,reverse = True)
    member = random.choice(member_list[:80])

    if member["user_id"] == event.user_id:
        msg = "不可以涩涩！"
    else:
        nickname = member['card'] or member['nickname']
        global record_yinpa
        record_yinpa.setdefault(member['user_id'],0)
        record_yinpa[member['user_id']] += 1
        membe = await bot.get_group_member_info(group_id = group_id, user_id = user_id)
        A = membe['card'] or membe['nickname']
        await yinpa.send(f"现在咱将随机抽取一位幸运裙友\n送给{A}色色！")
        # 休眠
        fuckingTime = random.randint(1,20)
        await asyncio.sleep(fuckingTime)
        # 容量
        capacity = random.uniform(1,100)
        
        msg = (
            f"好欸！{A}用时{fuckingTime}秒 \n,给 {nickname} 注入了{round(capacity,3)}毫升的脱氧核糖核酸",
            MessageSegment.image(file = await user_img(member["user_id"]))
            )
    await yinpa.finish(msg, at_sender=True)

# 查看涩涩记录

yinpa_list = on_command("涩涩记录",aliases = {"色色记录"}, permission=GROUP, priority = 10, block = True)

@yinpa_list.handle()
async def _(bot:Bot, event: GroupMessageEvent):
    member_list = await bot.get_group_member_list(group_id = event.group_id)
    member_list.sort(key = lambda x:x["last_sent_time"] ,reverse = True)
    record = []
    for member in member_list:
        nickname = member['card'] or member['nickname']
        global record_yinpa
        times = record_yinpa.get(member['user_id'],0)
        if times:
            record.append([nickname,times])
    else:
        record.sort(key = lambda x:x[1],reverse = True)

    msg_list =[]
    msg ="卡池：\n——————————————\n"
    for member in member_list[:80]:
        nickname = member['card'] or member['nickname']
        msg += f"{nickname}\n"
    else:
        output = text_to_png(msg[:-1])
        msg_list.append(
            {
                "type": "node",
                "data": {
                    "name": "卡池",
                    "uin": event.self_id,
                    "content": MessageSegment.image(output)
                    }
                }
            )

    msg =""
    for info in record:
        msg += f"【{info[0]}】\n今日被透 {info[1]} 次\n"
    else:
        if msg:
            output = text_to_png("涩涩记录：\n——————————————\n" + msg[:-1])
            msg_list.append(
                {
                    "type": "node",
                    "data": {
                        "name": "记录",
                        "uin": event.self_id,
                        "content": MessageSegment.image(output)
                        }
                    }
                )
        else:
            pass
    await bot.send_group_forward_msg(group_id = event.group_id, messages = msg_list)
    await yinpa_list.finish()

# 重置娶群友记录

@scheduler.scheduled_job("cron",hour = 0)
def _():
    global record_waifu,record_yinpa
    record_waifu = {}
    record_yinpa = {}