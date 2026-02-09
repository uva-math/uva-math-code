.PHONY: serve invalidate deploy autodeploy

serve:
	bundle exec jekyll serve --incremental

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
