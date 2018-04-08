venv:
	virtualenv -p python3 venv
	venv/bin/pip install paramiko

.PHONY: clean
clean:
	rm -r venv
