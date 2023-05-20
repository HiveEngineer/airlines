from setuptools import setup, find_packages
setup(
    name='etl.py',
    version='0.1',
    packages= find_packages(),
    include_package_data=True,
    install_requires=[
        'pyspark',
        'delta-spark',
    ],
    entry_points='''
        [console_scripts]
        etl= etl.py:main
    ''',
)