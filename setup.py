# read the contents of your README file
from pathlib import Path

from setuptools import setup

from gqlrequests import __version__

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="gqlrequests",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["gqlrequests"],
    package_data={"gqlrequests": ["py.typed"]},
    install_requires=[],
    license="MIT",
    version=__version__,
    description="A Python library for making GraphQL requests easier!",
    python_requires=">=3.8.0",
    author="BeatsuDev",
    author_email="",
    url="https://github.com/BeatsuDev/GraphQLRequests",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
