from distutils.core import setup
from Cython.Build import cythonize

setup(ext_modules = cythonize(["dbs.py", "proc_hands.py", "os_tools.py", "main.py"]))
