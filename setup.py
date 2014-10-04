# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


try:
    import pypandoc
    description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    with open('README.md', 'rb') as f:
        description = f.read()


setup(
    name='djangocms-placeholder-attr',
    version='1.0.3',
    license='MIT',
    description='Allow you to call a plugin model attribute from a placeholder in django-cms',
    long_description=description,
    author='Steeve',
    author_email='mo0ofier@gmail.com',
    include_package_data=True,
    url='https://github.com/WnP/djangocms-placeholder-attr',
    packages=find_packages(),
    install_requires=['django-cms>=3.0.5', ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
    zip_safe=False,
)

## Installation by Mauricio Aizga - @MaoAiz
