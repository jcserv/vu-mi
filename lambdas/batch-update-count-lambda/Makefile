ifneq (,$(wildcard ./.env))
    include .env
    export
endif

clean:
	rm aws_lambda_artifact.zip

install:
	pip3 install -t dependencies -r requirements.txt --platform manylinux2014_x86_64 --target ./dependencies --only-binary=:all:

build/deps: install
	cd dependencies && zip ../aws_lambda_artifact.zip -r .

compile: build/deps
	zip aws_lambda_artifact.zip -u lambda_function.py

upload:
	aws lambda update-function-code --function-name "${LAMBDA_FUNCTION_NAME}" --zip-file "fileb://aws_lambda_artifact.zip" --region "${AWS_REGION}"