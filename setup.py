from setuptools import setup

setup(
    name='cppcpyutils',
    version='0.1',
    description=
    'Python functions for image processing from Compact Plants Phenomics Center',
    url='http://github.com/CougPhenomics/cppcpyutils',
    author='Dominik Schneider',
    author_email='dominik.schneider@wsu.edu',
    license='MIT',
    packages=['cppcpyutils'],
    install_requires=["numpy","matplotlib","pandas"],
    zip_safe=False)
