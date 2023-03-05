clean:
    rm -rf build dist src/npr_cli.egg-info
    pip uninstall -y npr-cli

build: clean
    pip install --upgrade build twine
    python -m build

publish-testpypi: build
    python -m twine upload --repository testpypi dist/*
    pip install --index-url https://test.pypi.org/simple/ --no-deps npr-cli
    pip install -r requirements.test.in
    npr --help
	
build-test: build
    pip install -r requirements.test.in $(find -f dist/*whl)
    @just _test

build-publish-test: publish-testpypi _test

publish:
    python -m twine upload dist/*

test: _test

deps:
    pip install -r requirements.dev.in -e .

_test:
    pytest