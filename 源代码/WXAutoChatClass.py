from wxauto import WeChat
from AIAPIClass import AIAPI
import re

class WXAutoChat:
    """
    1.使用是如果是群聊:at=True会好一点
    2.可以在Monitor_Get_Infornation函数上加个时间限制，避免短时间频繁提问
    3.采用字典列表提取问题，避免相同同一个用户短时间提问相同的问题
    4.每件监听一个人/群新建一个类，避免聊天不一样
    """
    __AIAPI=None# api接口类
    __wx = WeChat()# 微信监听对象
    __Monitor_Remark_Name = None # 监测对象的"备注名",没有备注就是原名
    __Robot_Name = None #(把自己当成机器人)自己的名字，自动获取，在群自动匹配备注名
    __msgs = None# 临时获取所有新消息
    __Questions_List = list()  # 记录提问列表[{"问题人名","问题"},...]
    __answers=None# 调用返回的答案
    def __init__(self, api_key:str, base_url:str="https://api.deepseek.com",model:str="deepseek-chat",max_tokens:int=2048,temperature:float=1.3,stream:bool=False,messages:dict=None):
        """
        自己跳转AIAPIClass看
        """
        # 创建接口类对象
        self.__AIAPI=AIAPI(api_key,base_url,model,max_tokens,temperature,stream,messages)


    def Initialize_Parameter(self):
        """本来是想通过自动化发送消息自动获取自己的备注名，但是返回只有self，所以没吊用"""
        __wx = WeChat()  # 微信监听对象
        self.__wx.SendMsg(msg="调试自动化...", who="文件传输助手")
        msgs = self.__wx.GetAllMessage()
        for msg in msgs:
            if msg.type == 'self':
                print(f'发送名：{msg.info}')
                return

    def Monitor_Get_Infornation(self,Monitor_Remark_Name:str,robot_name:str="流萤猫猫",question_at:bool=True):
        """
        通过按键模拟+监听控件->获取新的消息。获取的效率低，但是获取的消息全面
        :param Monitor_Remark_Name: 监控的人名/备注名
        :param robot_name: 回复的人名/在该群的备注，机器人的本名/在这群的名字
        :param question_at: 接受的问题是否要求@机器人名，Flase则监听群所有的消息
        :return: 异常消息
        """
        try:
            self.__Robot_Name=robot_name#获取机器人名字
            # 监听
            self.__msgs=self.__wx.GetAllNewMessage(6)# 最多获取6条新消息就停止监听（群的话会有群名，解析后只有4条消息了），或者监听超过30秒
            if self.__msgs:  # 内容为空
                print("获取新消息成功，正在解析消息...")
            else:
                print("未出现新消息...")
            # print(self.__msgs)#验证
            # 重新获取完整的群名，群名有时候加了(人数)/补充完整的人名，以防对方改名加多了几个字
            for key, value in self.__msgs.items():
                # if re.match("主控群", key):#效率不高
                if Monitor_Remark_Name in key:  # 检查键是否包含子字符串
                    self.__Monitor_Remark_Name = key
                    break
            # print(self.__Monitor_Remark_Name)#验证
            #如果有新消息->获取人/群名：筛选消息
            if self.__Monitor_Remark_Name is not None:
                # print(self.__msgs[self.__Monitor_Remark_Name]) #获取该群或人的消息列表
                for msg in self.__msgs[self.__Monitor_Remark_Name]:
                    # 筛选@猫猫的消息加入问题列表
                    if msg.type == 'friend' and question_at and re.search(fr"@{robot_name}\u2005", msg.content):
                        # 有at去掉前面6个字符串，消息去空格（用于接受群消息）
                        # print(f'【{msg.sender}】{msg.content[6:]if msg.content.strip()[6:] else "主人找你"}')  # 发送者+发送内容
                        self.__Questions_List.append([msg.sender,msg.content[6:] if msg.content.strip()[6:] else "主人找你"])
                    elif msg.type == 'friend' and not question_at:
                        # 没at就直接匹配所有消息，消息去空格（用于接受个人消息）
                        # print(f'【{msg.sender}】{msg.content if msg.content.strip() else "主人找你"}')  # 发送者+发送内容
                        self.__Questions_List.append([msg.sender,msg.content if msg.content.strip() else "主人找你"])
                #重置临时变量
                self.__Monitor_Remark_Name = None#重置监听备注名
                self.__msgs=None# 重置临时消息获取
                print("开始处理问题列表")
            # print(self.__Questions_List)#验证
            return self.__Questions_List
        except Exception as e:
            # print(f"异常{e}")
            return e

    def Handle_Qusetion_Send_Answers(self,send_at:bool=True):
        """
        处理问题列表，将问题列表解析发送到接口/写死，然后发送
        :param send_at: 发送到时候是否@提问题的人
        :return: 异常消息
        """
        try:
            # 处理消息列表：接入api/写死
            if self.__Questions_List:  # 如果问题列表不为空
                for question in self.__Questions_List:
                    # print("问题:\n", question[1])  # 验证
                    # ----------------------------调用接口：多轮对话---------------------------------#
                    # self.__answers=self.__AIAPI.Client_Response_Content(question[1])
                    print(f"\033[1m\033[33m【{question[0]}】:\n\033[0m\033[34m{question[1]}\033[0m")#控制台输出问题和用户名
                    self.__answers=self.__AIAPI.Self_Definition_Filter_Questions(question[1])#吧 问题筛选后获取的
                    print(f"\033[1m\033[33m【{self.__Robot_Name}】:\n\033[0m\033[35m{self.__answers}\033[0m")#控制台输出答案
                    # 发送,at=None就是不at
                    self.__wx.SendMsg(msg=self.__answers, who=self.__Monitor_Remark_Name,at=question[0] if send_at == True else None)
                    # 清空请求列表
                    self.__Questions_List.clear()
                    return self.__answers#返回答案
        except Exception as e:
            # print(f"异常:{e}")
            return e



if __name__ == '__main__':
    wx = WXAutoChat("sk-da89aa72b93f490eb1a2a13d5af104e7")
    while True:
        wx.Monitor_Get_Infornation("陈玉华（华姐）", "༺༂༒꧁麟꧂༒༂༻", False)
        wx.Handle_Qusetion_Send_Answers(True)



