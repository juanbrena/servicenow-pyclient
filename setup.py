import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="servicenow-pyclient",
    version="0.0.1",
    author="Juan Brena",
    author_email="",
    description="A package to allow you to interact with the ServiceNow REST API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/juanbrena/servicenow-pyclient",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)