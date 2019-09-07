venv:
	virtualenv -p python3 venv
	venv/bin/pip install -r backend/requirements.txt

.PHONY: clean
clean:
	rm -r venv
