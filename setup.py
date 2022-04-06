#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import pkgutil
import re
import shutil
import sys
from codecs import open

from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install

requires = ["mesa >= 0.8.6", "geopandas", "libpysal", "rtree"]

version = ""
with open("mesa_geo/__init__.py", "r") as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE
    ).group(1)

with open("README.md", "r") as f:
    readme = f.read()


class DevelopCommand(develop):
    """Pre-installation for development mode."""

    def run(self):
        get_mesa_viz_files()
        develop.run(self)


class InstallCommand(install):
    """Pre-installation for installation mode."""

    def run(self):
        get_mesa_viz_files()
        install.run(self)


def get_mesa_viz_files():
    get_viz_server_file(
        package="mesa", server_file="visualization/ModularVisualization.py"
    )
    get_mesa_templates(package="mesa", template_dir="visualization/templates")


def get_viz_server_file(package, server_file):
    viz_server_file = pkgutil.get_data(package, server_file)
    with open(os.path.join("mesa_geo", server_file), "wb") as server_file:
        server_file.write(viz_server_file)


def get_mesa_templates(package, template_dir):
    pkg_dir = sys.modules[package].__path__[0]
    for subdir in os.listdir(os.path.join(pkg_dir, template_dir)):
        # do not copy modular_template.html to avoid being overwritten
        if os.path.isdir(os.path.join(pkg_dir, template_dir, subdir)):
            shutil.copytree(
                os.path.join(pkg_dir, template_dir, subdir),
                os.path.join("mesa_geo", template_dir, subdir),
                dirs_exist_ok=True,
            )


setup(
    name="mesa-geo",
    version=version,
    description="Agent-based modeling (ABM) in Python 3+",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Project GeoMesa Team",
    author_email="",
    url="https://github.com/projectmesa/mesa-geo",
    packages=find_packages(),
    package_data={
        "mesa_geo": [
            "visualization/templates/*.html",
            "visualization/templates/css/*",
            "visualization/templates/js/*",
            "visualization/templates/external/**/**/*",
        ],
    },
    include_package_data=True,
    install_requires=requires,
    keywords="agent based modeling model ABM simulation multi-agent",
    license="Apache 2.0",
    zip_safe=False,
    classifiers=[
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Life",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Natural Language :: English",
    ],
    cmdclass={
        "develop": DevelopCommand,
        "install": InstallCommand,
    },
)
