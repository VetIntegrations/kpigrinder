worker:
	celery -A kpigrinder worker --loglevel=debug

test:
	python -m pytest --pylama --bandit --cov=.

deps-compile:
	for name in common ci dev; do \
		pip-compile --no-emit-index-url requirements/$$name.in; \
	done
