include *.mk

VERSION := $(shell date +%Y%m%d%H%M)

worker:
	PYTHONPATH=${GHOSTDB_PATH} \
	GHOSTDB_DB_DSN=${GHOSTDB_DB_DSN} \
		celery -A kpigrinder worker --loglevel=debug --beat --purge

test:
	PYTHONPATH=${GHOSTDB_PATH} \
	GHOSTDB_DB_DSN=${GHOSTDB_DB_DSN_FOR_TEST} \
		python -m pytest \
			--pylama \
			--bandit \
			--cov=. \
			kpigrinder/${TEST}

deps-compile:
	for name in common ci dev; do \
		pip-compile --no-emit-index-url requirements/$$name.in; \
	done

build-image-celery-beat:
	PYPI_LOGIN=${PYPI_LOGIN} PYPI_PASSWORD=${PYPI_PASSWORD}
	docker build \
		--build-arg PYPI_LOGIN=${PYPI_LOGIN} \
		--build-arg PYPI_PASSWORD=${PYPI_PASSWORD} \
		-t kpigrinder-celery-beat \
		-f build/Dockerfile.celery-beat .
	docker tag kpigrinder-celery-beat "gcr.io/${GCP_PROJECT_ID}/kpigrinder-celery-beat:v0.0.${VERSION}"
	docker tag kpigrinder-celery-beat "gcr.io/${GCP_PROJECT_ID}/kpigrinder-celery-beat:latest"
	docker push "gcr.io/${GCP_PROJECT_ID}/kpigrinder-celery-beat:v0.0.${VERSION}"
	docker push "gcr.io/${GCP_PROJECT_ID}/kpigrinder-celery-beat:latest"

build-image-celery:
	PYPI_LOGIN=${PYPI_LOGIN} PYPI_PASSWORD=${PYPI_PASSWORD}
	docker build \
		--build-arg PYPI_LOGIN=${PYPI_LOGIN} \
		--build-arg PYPI_PASSWORD=${PYPI_PASSWORD} \
		-t kpigrinder-celery\
		-f build/Dockerfile.celery .
	docker tag kpigrinder-celery "gcr.io/${GCP_PROJECT_ID}/kpigrinder-celery:v0.0.${VERSION}"
	docker tag kpigrinder-celery "gcr.io/${GCP_PROJECT_ID}/kpigrinder-celery:latest"
	docker push "gcr.io/${GCP_PROJECT_ID}/kpigrinder-celery:v0.0.${VERSION}"
	docker push "gcr.io/${GCP_PROJECT_ID}/kpigrinder-celery:latest"

build-images: build-image-celery build-image-celery-beat
