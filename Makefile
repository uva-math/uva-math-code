.PHONY: serve serve-full invalidate deploy autodeploy deploy-local uva-arxiv

UVA_ARXIV_PYTHON ?= python3

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

uva-arxiv:
	$(UVA_ARXIV_PYTHON) scripts/uva_arxiv/cli.py $(ARGS)
