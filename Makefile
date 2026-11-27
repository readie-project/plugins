CLAUDE  ?= claude
PYTHON  ?= python3
# Every folder under plugins/ that holds a Claude Code manifest.
PLUGINS := $(patsubst %/.claude-plugin/plugin.json,%,$(wildcard plugins/*/.claude-plugin/plugin.json))

.PHONY: all validate help

all: validate ## Run every check that CI runs

validate: ## Validate every plugin and the marketplace, and check the marketplace lists them all
	$(PYTHON) scripts/check_marketplace.py
	@for plugin in $(PLUGINS); do \
		echo "$(CLAUDE) plugin validate --strict $$plugin"; \
		$(CLAUDE) plugin validate --strict $$plugin || exit 1; \
	done
	$(CLAUDE) plugin validate .

help: ## List available targets
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
