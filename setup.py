from pathlib import Path
from setuptools import setup

_classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Topic :: Software Development :: Libraries',
    'Topic :: Utilities',
]

REQUIREMENTS = Path('requirements.txt').read_text().splitlines()


def _version():
    with open('wolk.py') as fp:
        line = next(i for i in fp if i.startswith('__version__'))
        return line.strip().split()[-1].strip("'")


if __name__ == '__main__':
    setup(
        name='wolk',
        version=_version(),
        author='Tom Ritchford',
        author_email='tom@swirly.com',
        url='https://github.com/rec/wolk',
        tests_require=['pytest'],
        py_modules=['wolk'],
        description='Better os.walk',
        long_description=open('README.rst').read(),
        license='MIT',
        classifiers=_classifiers,
        install_requires=REQUIREMENTS,
        keywords=['os.walk'],
    )
