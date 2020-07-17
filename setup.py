from setuptools import find_packages, setup

setup(
    name='vivisect',
    author='The Vivisect Cats',
    author_email='',
    version='0.1.0',
    url='https://github.com/vivisect/vivisect',
    packages=find_packages(),
    zip_safe=False,
    description='Pure python disassembler, debugger, emulator, and static analysis framework',
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
    classifiers=[
        'Topic :: Security',
        'Topic :: Software Development :: Disassemblers',
        'Topic :: Software Development :: Debuggers',
        'Programming Language :: Python :: 2',
        'License :: OSI Approved :: Apache Software License',
    ]
)
