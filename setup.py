from setuptools import setup, find_packages

with open("./README.md", "r") as fh:
    long_description = fh.read()
setup(
    name="gguf_llama",
    version="0.0.16",
    packages=find_packages(),
    install_requires=[
        'util_helper>=0.0.3',
        'llama-cpp-python>=0.2.26',
    ],
    #package_data={'glai': ['back_end/model_db/gguf_models/*.json']},
    #include_package_data=True,
    author="Łael Al-Halawani",
    author_email="laelhalawani@gmail.com",
    description="Wrapper for simplified use of Llama2 GGUF quantized models.",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "License :: Free for non-commercial use",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=['llama', 'gguf', 'quantized models', 'llama gguf', 'cpu inference'],
    url="https://github.com/laelhalawani/gguf_llama",
)