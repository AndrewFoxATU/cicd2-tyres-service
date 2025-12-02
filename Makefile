APP = app.main:app
PID_FILE = .uvicorn.pid

install:
	python -m venv venv
	venv/Scripts/python -m pip install --upgrade pip
	venv/Scripts/python -m pip install -r requirements.txt
	@echo "Activate with: source venv/Scripts/activate"

run:
	venv/Scripts/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

start:
	nohup venv/Scripts/python -m uvicorn $(APP) --host 0.0.0.0 --port 8000 --reload \
	  > .uvicorn.out 2>&1 & echo $$! > $(PID_FILE)
	@echo "Uvicorn started (PID=$$(cat $(PID_FILE))) on http://localhost:8000"

stop:
	@if [ -f $(PID_FILE) ]; then \
	  kill $$(cat $(PID_FILE)) && rm -f $(PID_FILE) && echo "Uvicorn stopped."; \
	else \
	  echo "No PID file found. Did you use 'make start'?"; \
	fi

test:
	venv/Scripts/python -m pytest -q
