.PHONY: docs docs-clean docs-linkcheck

docs:
	$(MAKE) -C docs html
	@echo
	@echo "Docs built: docs/_build/html/index.html"

docs-clean:
	$(MAKE) -C docs clean

docs-linkcheck:
	$(MAKE) -C docs linkcheck
