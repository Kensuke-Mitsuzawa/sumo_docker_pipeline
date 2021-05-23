clean:
	rm -rf sumo_docker_pipeline-*
install:
	poetry install
	poetry build --format sdist
	tar -xvf dist/*-`poetry version -s`.tar.gz
	cd sumo_docker_pipeline-* && pip install -e .
	rm -rf sumo_docker_pipeline-*


