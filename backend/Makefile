run:
	export $(cat .env | xargs) && rails c
	uvicorn app:app --reload


run2:
	sudo env "PATH=$PATH" python helloWorld.py  --serial-port '/dev/ttyUSB0' 


