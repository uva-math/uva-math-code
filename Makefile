.PHONY: serve serve-full invalidate deploy autodeploy deploy-local uva-arxiv-check uva-arxiv-db-since uva-arxiv-db-since-dry uva-arxiv-roster-history uva-arxiv-source-smoke uva-arxiv-api-smoke

UVA_ARXIV_PYTHON ?= python3
UVA_ARXIV_SINCE_ARG = $(if $(SINCE),--since "$(SINCE)")

define jekyll_serve
	@mkdir -p /tmp/jekyll-status
	@echo "idle" > /tmp/jekyll-status/uva-math
	@trap 'rm -f /tmp/jekyll-status/uva-math' EXIT INT TERM; \
	bundle exec jekyll serve $(1) 2>&1 | while IFS= read -r line; do \
		printf '%s\n' "$$line"; \
		case "$$line" in \
			*"Regenerating:"*|*"Generating..."*) echo "building" > /tmp/jekyll-status/uva-math ;; \
			*"done in"*) echo "done" > /tmp/jekyll-status/uva-math ;; \
			*"ERROR"*) \
				case "$$line" in \
					*".well-known"*|*"ECONNRESET"*) ;; \
					*) echo "error" > /tmp/jekyll-status/uva-math ;; \
				esac ;; \
		esac; \
	done
endef

serve:
	$(call jekyll_serve,--incremental)

serve-full:
	$(call jekyll_serve,)

deploy:
	@echo "Committing changes..."
	@git add -A
	@git commit --verbose --signoff || echo "No changes to commit"
	@echo "Pushing to remote..."
	@git push
	@echo "Deployment complete!"

autodeploy:
	@git add -A
	@git commit -m "Update website content" || echo "No changes to commit"
	@git push

deploy-local:
	bundle exec jekyll build
	find _site -name "*.html" -type f -exec sh -c 'grep -v "^[[:space:]]*$$" "$$1" > "$$1.tmp" && mv "$$1.tmp" "$$1"' _ {} \;
	aws s3 sync ./_site/ s3://math.virginia.edu --delete --profile dept

uva-arxiv-check:
	$(UVA_ARXIV_PYTHON) scripts/uva_arxiv/check_env.py

uva-arxiv-db-since:
	$(UVA_ARXIV_PYTHON) scripts/uva_arxiv/update_arxiv_db.py since $(UVA_ARXIV_SINCE_ARG) $(ARGS)

uva-arxiv-db-since-dry:
	$(UVA_ARXIV_PYTHON) scripts/uva_arxiv/update_arxiv_db.py since $(UVA_ARXIV_SINCE_ARG) --dry-run $(ARGS)

uva-arxiv-roster-history:
	$(UVA_ARXIV_PYTHON) scripts/uva_arxiv/roster_history.py --dry-run $(ARGS)

uva-arxiv-source-smoke:
	@test -n "$(ID)" || { echo "ID is required, e.g. make uva-arxiv-source-smoke ID=2501.01234"; exit 2; }
	$(UVA_ARXIV_PYTHON) scripts/uva_arxiv/sources.py fetch --id "$(ID)" --dry-run $(ARGS)

uva-arxiv-api-smoke:
	@test -n "$(ID)" || { echo "ID is required, e.g. make uva-arxiv-api-smoke ID=2501.01234"; exit 2; }
	$(UVA_ARXIV_PYTHON) scripts/uva_arxiv/s2_client.py smoke --id "$(ID)" $(ARGS)
