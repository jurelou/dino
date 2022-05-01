include .env
# all:
# 	docker-compose up -d --build

all:
	mkdir -p ${ROOT_FOLDER} || true
	docker-compose -f docker-compose-dev.yml up -d

stop:
	docker-compose -f docker-compose-dev.yml down -v

rm:
	sudo rm -rf ${ROOT_FOLDER}/DINO_SPLUNK_UNIVERSAL_FORWARDER
	sudo rm -rf ${ROOT_FOLDER}/__DINO_TEMP

setup:
	git submodule update --init
	python3.8 -m venv env
	env/bin/pip install pip --upgrade
	env/bin/pip install -r requirements.txt
	env/bin/pip install -r requirements-dev.txt
	@echo "*====================================================*"
	@echo "| Done! Now run: source env/bin/activate             |"
	@echo "*====================================================*"

re: stop
	docker-compose -f docker-compose-dev.yml up -d --build --force-recreate


format:
	@tox