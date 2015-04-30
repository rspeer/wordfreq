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
    entry_points={
        'console_scripts': [
            'wordfreq-tokenize-twitter = wordfreq_builder.cli.tokenize_twitter:main',
            'wordfreq-build-deps = wordfreq_builder.cli.build_deps:main'
        ]
    }
)
