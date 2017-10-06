from distutils.core import setup
from Cython.Build import cythonize
# python setup.py build_ext --inplace
setup(ext_modules = cythonize(["dbs.py", "proc_hands.py", "os_tools.py"]))
