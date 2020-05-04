import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="thingsGate-lubusax", # Replace with your own username
    version="0.0.1",
    author="Lu Bu",
    author_email="lu.bu.sax@gmail.com",
    description="thingsGate package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lubusax/2005_thingsGate",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)