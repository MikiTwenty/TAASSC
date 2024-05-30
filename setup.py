# Standard Library
from setuptools import setup, find_packages


def read_file(filename):
    with open(filename, 'r') as file:
        return file.read()

# Read requirements from the requirements.txt file
def load_requirements(filename:str='requirements.txt') -> None:
    with open(filename, 'r') as file:
        return [line.strip() for line in file if line and not line.startswith("#")]

version = read_file('VERSION')
license_text = read_file('LICENSE')
long_description = read_file('README.md')
requirements = load_requirements()

setup(
    name = 'pyTAASSC',
    version = version,
    author = 'kkyle2',
    maintainer = 'Michele Ventimiglia',
    maintainer_email = 'michele.ventimiglia01@gmail.com',
    description = 'Tool for the Automatic Analysis of Syntactic Sophistication and Complexity.',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    packages = find_packages(where='src', include=['taassc']),
    package_dir = {'': 'src'},
    install_requires = requirements,
    classifiers = [
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.10'
    ],
    python_requires = '>=3.10',
    include_package_data = True,
    zip_safe = False,
    license = license_text,
    data_files = [('', ['README.md', 'LICENSE', 'VERSION'])],
)