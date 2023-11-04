#! /usr/bin/make 


.PHONY: help 
help:  ## Print the help documentation
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: tunnel_jupyter 
tunnel_jupyter: ## Open jupyter tunnel (run from mac)
	ssh -L9999:localhost:9999 airflow

.PHONY: jupyter 
jupyter: ## Run jupyter
	jupyter-lab  --port=9999  --NotebookApp.iopub_data_rate_limit=10000000000 --allow-root --no-browser --ip=0.0.0.0

.PHONY: ssh
ssh: ## SSH into the airflow compute engine
	ssh rob@dorob


