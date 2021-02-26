from setuptools import find_packages, setup
from os import path

dirn = path.abspath(path.dirname(__file__))
with open(path.join(dirn, 'README.md'), 'r') as fd:
    desc = fd.read()

setup(
    name='vivisect',
    author='Vivisect',
    author_email='',
    version='1.0.1',
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
        'pyasn1==0.4.5',
        'pyasn1-modules==0.2.4',
        'cxxfilt==0.2.1',
        'msgpack==1.0.0',
        'pycparser==2.20',
    ],
    extras_require={
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
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: Apache Software License',
    ],
    python_requires='>=3.6',
)
