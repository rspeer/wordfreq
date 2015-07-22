from setuptools import setup

setup(
    name="wordfreq_builder",
    version='0.1',
    maintainer='Luminoso Technologies, Inc.',
    maintainer_email='info@luminoso.com',
    url='http://github.com/LuminosoInsight/wordfreq_builder',
    platforms=["any"],
    description="Turns raw data into word frequency lists",
    packages=['wordfreq_builder'],
    install_requires=['msgpack-python', 'pycld2']
)
