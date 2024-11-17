# Load .env variables
include .env
export $(shell sed 's/=.*//' .env)

# Specify the shell to use
SHELL := /bin/bash

docker.login:
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(AWS_ACCOUNT).dkr.ecr.$(AWS_REGION).amazonaws.com

docker.tag:
	docker tag $(IMAGE_NAME):latest $(AWS_ACCOUNT).dkr.ecr.$(AWS_REGION).amazonaws.com/$(IMAGE_NAME):latest

docker.push:
	docker push $(AWS_ACCOUNT).dkr.ecr.$(AWS_REGION).amazonaws.com/$(IMAGE_NAME):latest

build:
	docker build --no-cache --platform linux/amd64 -t $(IMAGE_NAME) -f generate_dockerfile.dockerfile .

lambda.update-code:
	aws lambda update-function-code --function-name "$(IMAGE_NAME)" \
		--image-uri "$(AWS_ACCOUNT).dkr.ecr.$(AWS_REGION).amazonaws.com/$(IMAGE_NAME):latest"

lambda.update-configuration:
	# Update the lambda environment variables, check if the lambda is in update state
	@for i in {1..5}; do \
		status=$$(aws lambda get-function --function-name $(IMAGE_NAME) --query 'Configuration.[State, LastUpdateStatus]' --output text); \
		if [ "$$status" = "Active	Successful" ]; then \
			echo "Lambda function is active and successful. Performing the task..."; \
			aws lambda update-function-configuration \
				--function-name $(IMAGE_NAME) \
				--environment "Variables={S3_BUCKET=$(S3_BUCKET)}"; \
			break; \
		else \
			echo "Attempt $(i): Lambda function is not active or successful. Rechecking in 5 seconds..."; \
			sleep 5; \
		fi; \
	done

deploy: build docker.login docker.tag docker.push lambda.update-code lambda.update-configuration