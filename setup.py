from setuptools import setup, find_packages
import os

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pm2mp",
    version="0.1.0",
    author="MushroomSquad",
    author_email="donsudak@gmail.com",
    description="A Python wrapper for the pm2 API to manage and control pm2 processes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MushroomSquad/pm2mp",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "annotated-types==0.7.0",
        "pydantic==2.10.6",
        "pydantic_core==2.27.2",
        "typing_extensions==4.12.2",
    ],
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
