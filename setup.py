from setuptools import setup

with open('README.md', 'r',encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='fuzzy-httpserver',
    version='1.5.0',
    description='Fuzzy matching HTTP file server with autocomplete and fallback',
    author='PakCyberbot',
    author_email='pakcyberbot@pakcyberbot.com',
    url="https://github.com/PakCyberbot/fuzzy-httpserver",  
    project_urls={  
        "Source": "https://github.com/PakCyberbot/fuzzy-httpserver",
        "Bug Tracker": "https://github.com/PakCyberbot/fuzzy-httpserver/issues",
    },
    packages=['fuzzy_httpserver'],
    entry_points={
        'console_scripts': [
            'fuzzy-httpserver = fuzzy_httpserver.server:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.6',
    long_description=long_description,
    long_description_content_type='text/markdown',
)
