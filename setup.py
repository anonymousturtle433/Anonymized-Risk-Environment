from setuptools import setup, find_packages
with open("README.md","r") as f:
    long_description = f.read()

setup(
    name="gym_risk",
    version="0.0.1",
    install_requires=["gym", "numpy"],
    author="Anonymous",
    author_email="anonimized@anonemail.com",
    description="An OpenAI Gym wrapper for the Risk game",
    long_description=long_description,
    url="TBA",
    packages=find_packages(),
    include_package_data=True,
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
