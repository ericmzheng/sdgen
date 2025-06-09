from setuptools import setup, find_packages

setup(
    name="sdgen",
    version="0.1.0",
    description="A library for structured data generation, parsing, and serialization.",
    author="Eric Zheng",
    author_email="ericmzheng@ucla.edu",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pydantic>=2.0.0",
        "pyyaml",
    ],
    python_requires=">=3.10",
)
