include *.mk


worker:
	celery -A kpigrinder worker --loglevel=debug

test:
	PYTHONPATH=${GHOSTDB_PATH} \
	GHOSTDB_DB_DSN=${GHOSTDB_DB_DSN} \
		python -m pytest \
			--pylama \
			--bandit \
			--cov=. \
			kpigrinder/

deps-compile:
	for name in common ci dev; do \
		pip-compile --no-emit-index-url requirements/$$name.in; \
	done
