import os
from setuptools import setup

f = open(os.path.join(os.path.dirname(__file__), 'README.md'))
readme = f.read()
f.close()

setup(
    name='django-ajaximage-kernel72',
    version='0.2.7',
    description='Upload images and files via ajax. Images are optionally resized.',
    long_description=readme,
    author="kernel72",
    author_email='bradley.griffiths@gmail.com',
    url='https://github.com/bradleyg/django-ajaximage-kernel72',
    packages=['ajaximage'],
    include_package_data=True,
    install_requires=['Django', 'Pillow',],
    zip_safe=False
)
