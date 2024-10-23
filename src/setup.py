from setuptools import setup, Extension
import pybind11

ext_modules = [
    Extension(
        'independence_graph',
        ['independence_graph.cpp'],
        include_dirs=[pybind11.get_include(), pybind11.get_include(user=True)],
    ),
]

setup(
    name='independence_graph',
    ext_modules=ext_modules,
)
