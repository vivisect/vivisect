from distutils.core import setup

setup(name='vivisect',
      version='1.0',
      description='Python Distribution Utilities',
      author='invisig0th',
      # author_email='',
      url='http://visi.kenshoto.com/viki/Vivisect',
      packages=['cobra', 'Elf', 'envi', 'PE', 'vdb', 'visgraph',
                'vivisect', 'vqt', 'vstruct', 'vtrace'],
      classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2 :: Only'])
