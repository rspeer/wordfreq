PYTHON = python

all: build.ninja

# make sure this package is in 'develop' mode and up to date
wordfreq_builder.egg-info/PKG-INFO: setup.py
	$(PYTHON) setup.py develop

# build the Ninja file that will take over the build process
build.ninja: rules.ninja wordfreq_builder/ninja.py wordfreq_builder/config.py wordfreq_builder.egg-info/PKG-INFO
	$(PYTHON) -m wordfreq_builder.cli.build_deps rules.ninja > build.ninja

