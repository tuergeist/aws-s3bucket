import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aws-s3bucket",
    version="0.0.2",
    author="Christoph Becker",
    author_email="mail@ch-becker.de",
    description="An S3 Bucket up download helper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tuergeist/aws-s3bucket",
    project_urls={
        "Bug Tracker": "https://github.com/tuergeist/aws-s3bucket/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=['boto3', 'requests']
)