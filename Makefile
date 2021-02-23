include *.mk


worker:
	PYTHONPATH=${GHOSTDB_PATH} \
	GHOSTDB_DB_DSN=${GHOSTDB_DB_DSN} \
		celery -A kpigrinder worker --loglevel=debug --purge

test:
	PYTHONPATH=${GHOSTDB_PATH} \
	GHOSTDB_DB_DSN=${GHOSTDB_DB_DSN} \
		python -m pytest \
			--pylama \
			--bandit \
			--cov=. \
			kpigrinder/${TEST}

deps-compile:
	for name in common ci dev; do \
		pip-compile --no-emit-index-url requirements/$$name.in; \
	done
