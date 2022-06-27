import os

import setuptools

with open("README.md", encoding="utf-8") as fp:
    long_description = fp.read()


BASE_DIR: str = os.path.dirname(os.path.realpath(__file__))
requirements: dict[str, list] = {}
packages: dict[str, str] = {
    "all": "requirements.txt",
    "test": "requirements.test.txt",
    "cdk": "deployment/requirements.txt",
    "master": "lib/masterserver/requirements.txt",
    "storage": "lib/storage/requirements.txt",
    "backend": "lib/web-backend/requirements.txt",
}

for package, requirements_file_path in packages.items():
    path: str = os.path.join(BASE_DIR, requirements_file_path)
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as requirements_file:
            requirements[package] = requirements_file.readlines()
    else:
        requirements[package] = []


setuptools.setup(
    name="quakeservices",
    version="0.0.1",
    description="Quake 2 Master Server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Gary Brandon",
    extras_require=packages,
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
)
