run:
	python3 -m uvicorn main:app --reload

install:
	pip3 install -t dependencies -r requirements.txt --platform manylinux2014_x86_64 --target ./dependencies --only-binary=:all:

zip/deps:
	(cd dependencies; zip ../aws_lambda_artifact.zip -r .)

zip:
	zip aws_lambda_artifact.zip -u main.py