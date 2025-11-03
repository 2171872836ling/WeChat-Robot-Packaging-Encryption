"""
遇到的问题：
注意路径问题，cd：转到包/main的路径再打包，否则会报错不存在
注意PyArmor 混淆代码生成的dist中的main.py才是接下来的操作对象
exe程序在dist/dsit/main.exe
======================================================================================
1.使用 PyArmor （混淆+加密）其他模块的代码:
    （1）安装库：pip install pyarmor -i https://pypi.tuna.tsinghua.edu.cn/simple
    （2）调用命令：（安装的是8x新版的）pyarmor gen 其他模块.py,(调用7x久版pyarmor obfuscate mian.py)
    （3)生成的dist文件夹下有：其他模块.py。其中run...包是解密的，要打包进去
    （4）调整路径测试：其他模块.py是否能单独运行
    （5）有导包，导入其他模块的要注意路径问题
    （6）批量加密（直接加密文件夹，把文件夹内的全部加密）：pyarmor gen --expired 2025-05-20 --recursive .\projects
    （7）有效文件.py和running...

2.使用 Cython 将核心逻辑编译为 C 扩展（将核心代码改成.pyx，再结合setup.py，调用命令生成.py）：
    （1）安装库：pip install cython -i https://pypi.tuna.tsinghua.edu.cn/simple
    （2）核心代码.py后缀改成.pyx 文件（例如 Main.pyx）：
    （3）创建一个 setup.py 文件：
        from setuptools import setup
        from Cython.Build import cythonize
        setup(
            ext_modules=cythonize("./核心文件.pyx"),
        )
    （4）编译 Cython 文件（注意路径）：python ./setup.py build_ext --inplace
    （5）调整路径，测试编译后的模块
    （6）删除其他文件，有效文件后缀是.pyd



3.  （1）直接编译spec文件：pyinstaller AIAPIClass.spec
    （2）spec以当前路径为标准的，里面的内容要以spec为标准，可以使用../
    （3）打包 datas=[('../dist/*', 'dist')],把dist文件全部打包（路径,目录/文件）
    （4）hiddenimports一定要有所有的包
    （5）加密upx关了，防止加密包损坏

打包：pyinstaller --onefile main.py                                                                                                    hiddenimports=["module_name"],

                                                                                                    )
4.注意事项：
    （1）在早期版本中使用 PyInstaller 的加密功能（虽然效果有限）
    （2）没有任何方法可以完全防止反编译，但通过上述措施可以有效增加破解的难度，保护你的代码。
    （3）逆编译操作：读内存.pyx文件，再逆编译即可获得源代码
"""

key=自己改deepseek的密钥