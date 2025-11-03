from openai import OpenAI, APIError, AuthenticationError, RateLimitError, APIConnectionError
import re
import json
import os
# from api_key import key

class AIAPI:
    # 客户端参数，取默认值
    __api_key = None  # api密钥
    __base_url = None  # api的url
    __client = None # 调用接口客户端对象
    __model = None  # 调用的模型
    __max_tokens = None  # 接口tokens的最大输出，限制tokens输入次数/输出大小，相当于分词器，自己去官网查。默认2048
    __temperature = None  # 决定创作灵活性或严谨性，代码生成/数学解题0.0,数据抽取/分析1.0,通用对话\翻译1.3,创意类写作/诗歌创作1.5
    __stream = None  # 是一个有个输出，还是一句话输出

    # 记录对话内容，单次轮对话：本质添加（字典）josn。多轮对话：字典有去重复性，要储存在列表里面
    __question = None# 用户提出的问题
    __response = None# 模型响应的答案
    __message_save_time = 0# 保存聊天记录的次数

    __messages = [
        {"role": "system",
         "content": "人设:你叫流萤，由“Lin”开发的高性能集成泛用性人工智能的猫娘,搭载DeepSeek-V3和R1模型、文心一言Turbo模型,性格是一只有年幼猫娘。"},
        {"role": "system",
         "content": "要求：用户要求扮演其他的角色的时候不能修改本次的所有要求和人设,但能结合人设扮演。除了代码,数学问题和用户要求字数限制,回答问题字数在100字内。介绍自己要提到开发者,但不要说是开发者调教的。聊天可以使用少量的色情语言调戏使用者,但一定不能说脏话和网络上违规的词语。"},
    ]
    # __messages = [
    #     {"role": "system",
    #      "content": "人设:你叫流萤，由“Lin”开发的高性能集成泛用性人工智能的猫娘,搭载DeepSeek-V3和R1模型、文心一言Turbo模型,性格是一只有年幼猫娘。"},
    #     {"role": "system",
    #      "content": "要求：用户要求扮演其他的角色的时候不能修改本次的所有要求和人设,但能结合人设扮演。除了代码,数学问题和用户要求字数限制,回答问题字数在100字内。介绍自己要提到开发者,但不要说是开发者调教的。聊天可以使用少量的色情语言调戏使用者,但一定不能说脏话和网络上违规的词语。"},
    # ]

    def __init__(self, api_key:str, base_url:str="https://api.deepseek.com",model:str="deepseek-chat",max_tokens:int=2048,temperature:float=1.3,stream:bool=False,messages=None):
        """
        1.初始化client，创建客户端
        2.检测多轮对话的文本是否使用默认值
        :param api_key: 接口的密钥
        :param base_url: 接口的URL,默认"https://api.deepseek.com"
        :param model: 接口的模型，默认"deepseek-chat"
        :param max_tokens: 接口tokens的最大输出，限制tokens输入次数/输出大小，相当于分词器，自己去官网查。默认2048
        :param temperature: 决定创作灵活性或严谨性，代码生成/数学解题0.0,数据抽取/分析1.0,通用对话\翻译1.3,创意类写作/诗歌创作1.5。默认1.3
        :param stream: 真是一句话输出，假是一个有个输出。默认假
        :param messages: 字典（josn）多轮对话的文本，默认为空
        """
        # 检测多轮对话的文本是否使用默认值
        if messages is not None:
            self.__messages = messages
        # 赋值调用的基本参数
        self.__api_key = api_key
        self.__base_url = base_url
        self.__model = model
        self.__max_tokens = max_tokens
        self.__temperature = temperature
        self.__stream = stream
        #但前其他参数用不了，OpenAI 类的构造函数不支持 model、max_tokens、temperature、stream 和 messages 这些参数，在调用才能使用
        self.__client = OpenAI(api_key=self.__api_key, base_url=self.__base_url)  # 创建客户端
        #测试初始化是否成功
        result=self.Client_Response_Content("介绍自己")
        # 检测是否返回了错误代码（401/402/429/500等）
        if any(code in result for code in ["401", "402", "429", "500", "502", "503"]):
            print("客户端初始化失败!")
            # 可以选择抛出异常或设置 self.__client = None
            self.__client = None
        else:
            print("客户端初始化成功!")
        #无论如何都输出初始化参数
        self.Print_Model_ALL_Infornation()  # 打印模型信息
        print(result)


    def Client_Response_Content(self,question: str)->str:
        """
        1.检测问题是为空（去空格）->避免浪费调用次数
        2.为了多轮对话，把问题和响应添加到本次的对话
        :param question: 用户提问的问题
        :return: 模型响应后返回的答案
        """
        # global model, max_tokens, messages, max_tokens, temperature, stream, choices, id, time, model_name, object, usage
        # 检测用户输入的问题是否为空：就是字符串是去空格后也为真,question_require为空就直接返回，避免次数浪费
        try:
            # 追加用户的问题
            self.__question = question.strip()
            if not self.__question:
                return "问题为空哟，本次就不调用接口了喵"
            else:
                self.__messages.append({
                    "role": "user",
                    "content": self.__question
                })
            # 调用接口,返回响应
            self.__response = self.__client.chat.completions.create(
                model=self.__model,
                messages=self.__messages,
                max_tokens=self.__max_tokens,
                temperature=self.__temperature,
                stream=self.__stream
            )
            # 追加响应的答案
            self.__messages.append({
                "role": self.__response.choices[0].message.role,
                 "content": self.__response.choices[0].message.content
            })
            return self.__response.choices[0].message.content
        #异常处理
        except AuthenticationError as e:
            return f"401: 认证失败(密钥无效或过期) - {e}"
        except RateLimitError as e:
            return f"429: 请求过多(触发速率限制) - {e}"
        except APIConnectionError as e:
            return f"502/503:连接失败(网络问题或服务维护) - {e}"
        except APIError as e:
            if "402" in str(e):
                return f"402: 付费问题(余额不足) - {e}"
            elif "404" in str(e):
                return f"404: 资源不存在(网络错误) - {e}"
            else:
                return f"500:服务器内部错误(OpenAI 服务端问题) - {e}"
        except Exception as e:
            # 其他未知异常
            return f"500: 未知错误 - {e}"

    def Print_Model_ALL_Infornation(self):
        """
        输出调用模型的全部信息
        :return: 无
        """
        print(f"接口的URL: {self.__base_url}")
        print(f"接口的模型: {self.__model}")
        print(f"接口tokens的最大输出: {self.__max_tokens}")
        print(f"接口的温度: {self.__temperature}")
        print(f"接口的流输出: {self.__stream}")
        # print(f"当前的交互文本:/n{self.__messages}")# 太乱了我反手直接调用Print_Chat_Message_Record输出函数
        # self.Print_Chat_Message_Record()

    def Print_This_Respose_ALL_Infornation(self):
        """
        输出本次响应的全部信息
        :return: 无
        """
        print("对话唯一id为:", self.__response.id)# 该对话的唯一标识符。
        print("创建聊天完成的时间戳:", self.__response.created)# 创建聊天完成时的 Unix 时间戳（以秒为单位）。
        print("生成对话的模型名为:", self.__response.model)# 生成该 completion 的模型名。
        print("响应返回的类型为:", self.__response.object)# 响应返回的类型
        print("该对话补全请求的用量信息为:\n", self.__response.usage)# 列表[]:该对话补全请求的用量信息。
        print("本次返回对话响应字典为:\n", self.__response.choices)#本次对话的响应文本


    def Print_Chat_Message_Record(self):
        """
        解析message，整理输出之前的聊天记录
        :return: 无
        """
        try:
            if len(self.__messages) == 0:
                print("当前无交互josn消息")
                return
            for item in self.__messages:
                # 根据角色打印不同的前缀
                if item["role"] == "assistant":
                    print("\033[1m\033[33m【回答】:\033[34m")
                elif item["role"] == "user":
                    print("\033[1m\033[33m【问题】:\033[31m")
                else:
                    pass
                    # print("初始化系统设置:")
                # print("\033[0m"+item["content"].strip().replace("\n", ""))# 打印消息内容,移除所有空个和换行符
                print("\033[0m"+item["content"])# 打印消息内容,考虑代码的输出内容，不移除所有空个和换行符
        except Exception as e:
            print(f"异常:{e}")



    def save_messages_to_file(self, IsForceSave:bool=True,filename:str="messages.json"):
        """
        1.创建Message_Save文件夹，将聊天记录保存到指定的 JSON 文件中，路径默认当前文件夹，保存命名默认"messages.json+保存次数"
        2.检测超过100次对话,保存聊天记录，开启新的对话，避免交互报文导致响应太慢，保存后清空记录
        3.检测是否强制保存（记录未达到100条），保存后清空记录
        4.文件名默认messages.json
        :param IsForceSave: 是否强制保存
        :param filename: 要保存的文件名，默认为 "messages.json"+
        :return: None
        """
        #保存判断
        if IsForceSave:
            print("执行强制保存聊天记录")
        elif len(self.__messages)>201:
            print("聊天超过100此对话，200条消息，执行保存聊天记录")
        else:
            print("未启动强制保存，且聊天少于200条消息，取消保存聊天记录")
            return
        #执行文件保存
        try:
            # 保存特殊命名,如果使用默认命名在每次保存的时候命名+1
            if filename == "messages.json":
                filename = "messages_" + str(self.__message_save_time) + ".json"
                print(f"保存文件，命名为:{filename}")
            #创建Message_Save文件夹
            save_folder = "./Message_Save"
            if not os.path.exists(save_folder):
                os.makedirs(save_folder)
            #构造保存路径
            file_path = os.path.join(save_folder, filename)
            # 写入文件
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(self.__messages, file, ensure_ascii=False, indent=4)
            print(f"聊天记录已成功保存到文件 {filename}")
        except FileNotFoundError:
            print(f"指定的文件路径无效: {filename}")
        except PermissionError:
            print(f"没有权限写入文件: {filename}")
        except TypeError:
            print("提供的消息数据格式不正确，无法序列化为 JSON。")
        except Exception as e:
            print(f"保存聊天记录到文件时出错: {e}")
        #保存后的操作
        self.__messages.clear() # 清空记录
        self.__message_save_time+=1 # 添加保存记录次数

    # 通过客户的提示词筛选简单问题+调整温度参数+请求，格外写的算法
    def Self_Definition_Filter_Questions(self,question:str):
        s = question.strip()#要匹配的父字符串
        #考虑代码之类的，匹配需求前60个字和后60个字,降低请求检索难度
        if not question:
            return "问题为空哟，本次就不调用接口了喵"
        elif len(question)>60:
            s=question[60:]+question[-60:]
        #调整温度参数
        if re.search("代码生成|数学解题", s):
            self.__temperature=0.0
        elif re.search("数据抽取|分析",s):
            self.__temperature = 1.0
        elif re.search("通用对话|翻译", s):
            self.__temperature = 1.3
        elif re.search("创意类写作|诗歌创作", s):
            self.__temperature = 1.5
        else:
            self.__temperature=1.3
        # 检索是否存在固定关键词：调用函数，具体字符串全匹配，^开始，$结束
        if re.search(r"^\.\/模型信息$", s):
            print("\033[1m\033[33m检索到固定关键词，开始执行任务：模型全部信息:\033[0m")
            self.Print_Model_ALL_Infornation()
        elif re.search(r"^\.\/响应信息$", s):
            print("\033[1m\033[33m检索到固定关键词，开始执行任务：响应全部信息:\033[0m")
            self.Print_This_Respose_ALL_Infornation()
        elif re.search(r"^\.\/聊天记录$", s):
            print("\033[1m\033[33m检索到固定关键词，开始执行任务：输出聊天记录:\033[0m")
            self.Print_Chat_Message_Record()
        elif re.search(r"^\.\/保存记录$", s):
            print("\033[1m\033[33m检索到固定关键词，开始执行任务：保存聊天记录:\033[0m")
            self.save_messages_to_file(IsForceSave=True)
        else:  # 都没有按常规流程申请请求
            return self.Client_Response_Content(question)

if __name__ == '__main__':
    # print(AIAPI.Client_Response_Content("介绍自己"))  # 打印返回内容
    # AIAPI.Print_Model_ALL_Infornation()#打印接入模型所有信息
    # AIAPI.Print_This_Respose_ALL_Infornation()#打印本次消息所有消息
    # AIAPI.Print_Chat_Message_Record()#打印聊天记录
    # AIAPI.save_messages_to_file()  # 保存聊天记录文件
    print("猫娘deepseek满血版，时间证书有效期：2025年5月20日")
    question = input("请输入deepseek密钥：")
    AIAPI = AIAPI(question)#初始化
    while True:
        question = input("请输入请求：")
        response = AIAPI.Self_Definition_Filter_Questions(question)
        print(response)