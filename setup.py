from setuptools import find_packages, setup
from os import path

VERSION = '1.0.4'

dirn = path.abspath(path.dirname(__file__))
with open(path.join(dirn, 'README.md'), 'r') as fd:
    desc = fd.read()

setup(
    name='vivisect',
    author='The Vivisect Peeps',
    author_email='',
    version=VERSION,
    url='https://github.com/vivisect/vivisect',
    packages=find_packages(),
    zip_safe=False,
    description='Pure python disassembler, debugger, emulator, and static analysis framework',
    long_description=desc,
    long_description_content_type='text/markdown',
    include_package_data=True,
    package_data={
        '': ['*.dll', '*.dylib', '*.lyt', 'Makefile', '*.c', '*.h', '*.yes', '*.sh']
    },
    entry_points={
        'console_scripts': [
            'vivbin=vivisect.vivbin:main',
            'vdbbin=vdbbin.vdbbin:main',
        ]
    },
    install_requires=[
        'pyasn1>=0.4.5,<0.5.0',
        'pyasn1-modules>=0.2.4,<0.3.0',
        'cxxfilt>=0.2.1,<0.3.0',
        'msgpack>=1.0.0,<1.1.0',
        'pycparser>=2.20',
    ],
    extras_require={
        'docs': [
            'sphinx>=1.8.2,<2.0.0',
            'sphinx-rtd-theme>=0.4.2,<1.0.0',
        ],
        'gui': [
            'pyqt5==5.15.1',
            'pyqtwebengine==5.15.1',
        ]
    },
    classifiers=[
        'Topic :: Security',
        'Topic :: Software Development :: Disassemblers',
        'Topic :: Software Development :: Debuggers',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: Apache Software License',
    ],
    python_requires='>=3.6',
)
