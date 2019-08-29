from setuptools import setup, find_packages

setup(
    name         = 'abrds',
    version      = '1.3',
    packages     = find_packages(),
    entry_points = {'scrapy': ['settings = abrds.settings']},
    include_package_data = True
)