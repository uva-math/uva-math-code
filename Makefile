.PHONY: serve invalidate deploy

serve:
	bundle exec jekyll serve --incremental

deploy:
	@echo "Committing changes..."
	@git add -A
	@git commit --verbose --signoff || echo "No changes to commit"
	@echo "Pushing to remote..."
	@git push
	@echo "Deployment complete!"
