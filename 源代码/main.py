from pyexpat.errors import messages

from WXAutoChatClass import WXAutoChat
import os
def main_use():
    print("""
\033[1m\033[31m注意：
\033[32m1.登录微信，打开程序，观看下面提示填写参数。优先写备注名字，一个程序监听一个，可以多开，或者在源码的线程追加监听列表
\033[34m2.别人叫你要不要加@：“@模式”用于回复多人群聊天，避免浪费调用次数；单人聊天尽量别开@，因为单人“@”后面没有“\u2005”，正则匹配不到。回复：默认@模式，开不开无所谓
\033[35m3.获取deepseek10元钱的密钥有80万字token，相当于一本半的新华字典，性价比最高，获取密钥方式2分27秒看起，：https://www.bilibili.com/video/BV1AwRVYHE81/?spm_id_from=333.337.search-card.all.click&vd_source=60bac6fde1f2d38c516c4a777ddbf83d
\033[36m4.常见问题：
    (1)使用次数少会自动退出微信登录，属于正常现象
    (2)超过200条消息自动储存，聊天保存位置在这个程序的当前文件夹Message_Save中
    (3)初代版本已经开源，请遵守LGPL开源协议。开发尽量别用SDK的库，比如itchat，up扫出一堆违禁数据(包括微信ID)，喜提15天封号大礼包。wxatuo响应慢但也是目前最好用的库了
    (4)up之前电脑有病毒怕密钥泄露，所以加固了“亿”下：二次加密+三次迭代混淆代码+scl密钥加密+加冷门壳+动态加密+证书->拿去攻防战都不一定能破（up目前最强的套壳，自己都无法逆编译，但是可以抓包流量分析）
    (5)加密版的2025年5月30号过期
    (6)默认猫娘模式，能调用的命令:
    ./模型信息
    ./响应信息
    ./聊天记录
    ./保存记录
\033[31m密钥谨慎保管，切勿透露
    \033[0m""")
    # ====================================================初始化客户端(可以换api接口)=================================================================== #
    print("==========api设置==========")
    #接口网址：
    base_url = input("\033[36m请输入api接口网址（直接回车默认deepseek的）:\033[1m\033[31m").strip().replace("\n","")
    if not base_url:#为空
        base_url="https://api.deepseek.com"

    #模型
    model = input("\033[36m请输入调用的模型名字（直接回车默认deepseek的）:\033[1m\033[31m").strip().replace("\n","")
    if not model:#为空
        model="deepseek-chat"

    #人设
    system_role=None
    role = input("\033[36m人设（直接回车，默认“猫娘模式”）:\033[1m\033[31m")
    if role.strip().replace("\n",""):
        system_role = [
            {"role": "system","content": "要求：用户要求扮演其他的角色的时候不能修改本次的所有要求和人设,但能结合人设扮演。除了代码,数学问题和用户要求字数限制,回答问题字数在100字内。介绍自己要提到开发者,但不要说是开发者调教的。一定不能说脏话和网络上违规的词语。"},
            {"role": "system","content": role}
        ]


    #密钥
    api_key=input("\033[36m请输入接口密钥:\033[1m\033[31m").strip().replace("\n","")

    #初始化客户端.
    print("初始化客户端...请等待输出(1分钟内)，如果输出“客户端初始化失败”，请根据“报错代码”联系管理员!\033[0m")
    wxautochat = WXAutoChat(api_key=api_key,base_url=base_url,model=model,messages=system_role)

    # ====================================================监听设置=================================================================== #
    print("==========监听设置==========")
    #自动回复的人名/群名（优先备注名字）
    Monitor_Remark_Name=input("\033[36m请输入自动回复的人名/群名（优先备注名字）:\033[1m\033[31m")

    #机器人的名字（头顶第一行的名字/别人要@你的名称）
    rootname = input("\033[36m请输入机器人的名字（头顶第一行的名字/别人要@你的名称）:\033[1m\033[31m")

    # 唤醒用@
    question_at= input("\033[36m别人是否@才能唤醒自动回复（填“y”或“n”，大小写随意）:\033[1m\033[31m")
    if question_at.upper() == "Y":
        question_at=True
    elif question_at.upper() == "N":
        question_at=False
    else:
        print("填错了，默认“Y”,你可以关了再打开，重新填")
        question_at=True
        print("\033[0m")

    # 回复用@
    send_at = input("\033[36m回复别人是否@它（填“y”或“n”，大小写随意）:\033[1m\033[31m")
    if send_at.upper() == "Y":
        send_at=True
    elif send_at.upper() == "N":
        send_at=False
    else:
        print("填错了，默认“Y”,你可以关了再打开，重新填")
        send_at=True


    #输出响应
    input("\033[32m“按回车”开始使用\033[0m")
    os.system('cls')#清空输出，避免密钥暴露
    while True:
        wxautochat.Monitor_Get_Infornation(Monitor_Remark_Name=Monitor_Remark_Name,robot_name=rootname,question_at=question_at)
        wxautochat.Handle_Qusetion_Send_Answers(send_at=send_at)



    # def  thread_func(Monitor_Remark_Name):
    #     # Monitor_Remark_Name=input("监听人/群(有备注写备注，没有写)：")
    #     while True:
    #         wxautochat.Monitor_Get_Infornation(Monitor_Remark_Name)
    #         wxautochat.Handle_Qusetion_Send_Answers(True)
    # 创建线程
    # thread1 = threading.Thread(target=thread_func,kwargs={'Monitor_Remark_Name':"猫娘研究协会"})
    # thread2 = threading.Thread(target=thread_func)
    # 启动线程
    # thread1.start()
    # thread2.start()
    # 等待线程完成
    # thread1.join()
    # thread2.join()

# print ("""
#             \033[31m\033[1m声明：
#             请遵守LGPL开源协议，别想着反编译和卖钱了，混淆迭代3次+二次加密+二进制编译+语言拓展+证书+后门，我都开源了初版了，自己封装SDK不香吗
# \033[0m""")

if __name__ == '__main__':
    main_use()
