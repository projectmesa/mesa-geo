#!/usr/bin/env python
import base64
import hashlib
import os
import re
import shutil
import urllib.request
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py


def get_version_from_package() -> str:
    with open("mesa_geo/__init__.py") as fd:
        version = re.search(
            r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE
        ).group(1)
    return version


class BuildPyCommand(build_py):
    def run(self):
        get_frontend_dep()
        build_py.run(self)


def get_frontend_dep():
    # Important: Make sure to update the integrity_hash together with the new version number,
    # otherwise the previous file is going to be kept and used.
    leaflet_version = "1.8.0"
    ensure_frontend_dep_single(
        f"https://unpkg.com/leaflet@{leaflet_version}/dist/leaflet.js",
        external_dir_single=Path("mesa_geo/visualization/templates/js/external"),
        integrity_hash="sha512-BB3hKbKWOc9Ez/TAwyWxNXeoV9c1v6FIeYiBieIWkpLjauysF18NzgR1MBNBXf8/KABdlkX68nAhlwcDFLGPCQ==",
    )
    ensure_frontend_dep_single(
        f"https://unpkg.com/leaflet@{leaflet_version}/dist/leaflet.css",
        external_dir_single=Path("mesa_geo/visualization/templates/css/external"),
        integrity_hash="sha512-hoalWLoI8r4UszCkZ5kL8vayOGVae1oxXe/2A4AO6J9+580uKHDO3JdHb7NzwwzK5xr/Fs0W40kiNHxM9vyTtQ==",
    )


def make_hash(filepath):
    with open(filepath, "rb") as f:
        file_as_bytes = f.read()
    file_hash = base64.b64encode(hashlib.sha512(file_as_bytes).digest())
    return "sha512-" + file_hash.decode()


def ensure_frontend_dep_single(
    url, external_dir_single, out_name=None, integrity_hash=None
):
    external_dir_single.mkdir(parents=True, exist_ok=True)
    # Used for downloading e.g. Leaflet single file
    if out_name is None:
        out_name = url.split("/")[-1]
    dst_path = external_dir_single / out_name
    print(f"Checking for presence of {dst_path=} {dst_path.is_file()=}")

    if not dst_path.is_file():
        download_frontend_dep_single(url, dst_path, out_name, integrity_hash)
        return

    if integrity_hash is None:
        # File is present and assumed to be valid
        print(f"{out_name} is present and assumed to be valid; not downloading")
        return

    if make_hash(dst_path) == integrity_hash:
        # File is present and confirmed valid
        print("{out_name} is present and confirmed valid; not downloading")
        return

    download_frontend_dep_single(url, dst_path, out_name, integrity_hash)


def download_frontend_dep_single(url, dst_path, out_name, integrity_hash):
    print(f"Downloading the {out_name} dependency from the internet...")
    urllib.request.urlretrieve(url, out_name)
    if integrity_hash and ((actual_hash := make_hash(out_name)) != integrity_hash):
        os.remove(out_name)
        raise ValueError(
            f"Integrity check failed for {out_name}. Expected {integrity_hash}, "
            f"received {actual_hash}."
        )
    shutil.move(out_name, dst_path)


if __name__ == "__main__":
    setup(
        name="Mesa-Geo",
        version=get_version_from_package(),
        cmdclass={
            "build_py": BuildPyCommand,
        },
    )
