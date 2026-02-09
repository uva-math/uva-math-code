.PHONY: serve invalidate deploy autodeploy deploy-local

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

deploy-local:
	bundle exec jekyll build
	find _site -name "*.html" -type f -exec sh -c 'grep -v "^[[:space:]]*$$" "$$1" > "$$1.tmp" && mv "$$1.tmp" "$$1"' _ {} \;
	aws s3 sync ./_site/ s3://math.virginia.edu --delete --profile dept
