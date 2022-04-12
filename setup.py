#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import hashlib
import os
import pkgutil
import re
import shutil
import sys
import urllib.request
from distutils.command.build import build

from setuptools import setup
from setuptools.command.develop import develop


def get_version_from_package() -> str:
    with open("mesa_geo/__init__.py", "r") as fd:
        version = re.search(
            r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE
        ).group(1)
    return version


class DevelopCommand(develop):
    """Installation for development mode."""

    def run(self):
        get_mesa_viz_files()
        get_frontend_dep()
        develop.run(self)


class BuildCommand(build):
    """Command for build mode."""

    def run(self):
        get_mesa_viz_files()
        get_frontend_dep()
        build.run(self)


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


def get_frontend_dep():
    # Important: Make sure to update package_includes with the new version number in
    # mesa_geo/visualization/modules/MapVisualization.py,
    # and the hardcoded css file in mesa_geo/visualization/templates/modular_template.html.
    leaflet_version = "1.8.0"
    ensure_frontend_dep_single(
        f"https://unpkg.com/leaflet@{leaflet_version}/dist/leaflet.js",
        out_name=f"leaflet-{leaflet_version}.js",
        external_dir_single="mesa_geo/visualization/templates/js/external",
        integrity_hash="sha512-BB3hKbKWOc9Ez/TAwyWxNXeoV9c1v6FIeYiBieIWkpLjauysF18NzgR1MBNBXf8/KABdlkX68nAhlwcDFLGPCQ==",
    )
    ensure_frontend_dep_single(
        f"https://unpkg.com/leaflet@{leaflet_version}/dist/leaflet.css",
        out_name=f"leaflet-{leaflet_version}.css",
        external_dir_single="mesa_geo/visualization/templates/css/external",
        integrity_hash="sha512-hoalWLoI8r4UszCkZ5kL8vayOGVae1oxXe/2A4AO6J9+580uKHDO3JdHb7NzwwzK5xr/Fs0W40kiNHxM9vyTtQ==",
    )


def ensure_frontend_dep_single(
    url, external_dir_single, out_name=None, integrity_hash=None
):
    os.makedirs(external_dir_single, exist_ok=True)
    # Used for downloading e.g. Leaflet single file
    if out_name is None:
        out_name = url.split("/")[-1]
    dst_path = os.path.join(external_dir_single, out_name)
    if os.path.isfile(dst_path):
        return
    urllib.request.urlretrieve(url, out_name)
    if integrity_hash:
        with open(out_name, "rb") as f:
            bytes = f.read()
        actual_hash = base64.b64encode(hashlib.sha512(bytes).digest())
        actual_hash = "sha512-" + actual_hash.decode()
        if actual_hash != integrity_hash:
            os.remove(out_name)
            raise ValueError(
                f"Integrity check failed for {out_name}. Expected {integrity_hash}, received {actual_hash}."
            )
    shutil.move(out_name, dst_path)


if __name__ == "__main__":
    setup(
        name="Mesa-Geo",
        version=get_version_from_package(),
        cmdclass={
            "develop": DevelopCommand,
            "build": BuildCommand,
        },
    )
