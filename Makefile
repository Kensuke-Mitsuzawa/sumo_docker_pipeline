clean:
	rm -rf sumo_docker_pipeline-*
install:
	poetry install
	poetry build --format sdist
	tar -xvf dist/*-`poetry version -s`.tar.gz
	cd sumo_docker_pipeline-* && pip install -e .
test:
	pytest --workers 3 tests
	cd examples/ && python example_script.py
	pytest --nbmake examples/
