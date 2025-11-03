from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(["./WXAutoChatClass.pyx","./AIAPIClass.pyx","./api_key.pyx"]),
)