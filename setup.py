from distutils.core import setup
import multitest
setup(
    name = 'multitest',
    description='Multiprocess Unittest Runner',
    license='MIT License',
    version=multitest.__version__,
    author='tcooc',
    author_email='thcooc@gmail.com',
    url='https://github.com/tcooc/multitest',
    packages=['multitest'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Software Development :: Testing',
    ],
)
