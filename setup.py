import pathlib
from setuptools import setup, find_packages

BASE = pathlib.Path(__file__).parent

README = (BASE / "README.md").read_text()
print(README)
setup(
    name='cloud-workflows',
    version='0.0.1',
    description='Unoffical SDK for Cloud Workflows',
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/zdenulo/cloud-workflows",
    author="Zdenko Hrček",
    author_email="zdenulo@gmail.com",
    license="MIT",
    classifiers=[
        'Development Status :: 3 - Alpha',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=["pyyaml", "yamlable"],
)
