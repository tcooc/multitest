from setuptools import setup
import multitest
setup(
    name='multitest',
    description='Multiprocess Unittest Runner',
    long_description='Extends the standard unittest library to run on multiple processes.',
    license='MIT License',
    version=multitest.__version__,
    author=multitest.__author__,
    author_email=multitest.__email__,
    url='https://github.com/tcooc/multitest',
    download_url='https://pypi.python.org/pypi/multitest',
    packages=['multitest'],
    platforms=['any'],
    keywords='unittest test multiprocessing',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Testing',
    ],
)
