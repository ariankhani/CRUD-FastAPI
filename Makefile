.PHONY: isort
isort:
	ruff check --select I --fix
.PHONY: check
check:
	ruff check
.PHONY: check-fix
check-fix:
	ruff check --fix 
.PHONY: check-imports
check-imports:
	ruff check --select F401 --fix