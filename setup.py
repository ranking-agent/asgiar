"""Setup file for asgiar package."""
from setuptools import setup

setup(
    name='asgiar',
    version='0.2.1',
    author='Patrick Wang',
    author_email='patrick@covar.com',
    url='https://github.com/patrickkwang/asgiar',
    description='ASGIAR',
    packages=['asgiar'],
    include_package_data=True,
    install_requires=[
        "httpx>=0.18"
    ],
    zip_safe=False,
    license='MIT',
    python_requires='>=3.6',
)
