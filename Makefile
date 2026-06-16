load:
	python src/etl/loader.py

test:
	pytest

report:
	python src/reporting/generate_reports.py

dashboard:
	streamlit run app.py

api:
	uvicorn api.main:app --reload

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +