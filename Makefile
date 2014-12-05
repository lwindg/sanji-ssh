all: pylint test

pylint:
	flake8 --exclude=tests,.git -v .
test:
	nosetests --with-coverage --cover-package=ssh

.PHONY: pylint test
