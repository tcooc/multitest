from distutils.core import setup
import multitest
setup(
    name = 'multitest',
    description='Multiprocess Unittest Runner',
    license='MIT License',
    version=multitest.__version__,
    author=multitest.__author__,
    author_email=multitest.__email__,
    url='https://github.com/tcooc/multitest',
    packages=['multitest'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Testing',
    ],
)
