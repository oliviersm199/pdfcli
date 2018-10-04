init:
	pip install -r requirements.txt

test:
	python tests.py

package:
	python setup.py bdist_wheel

upload:
	python setup.py upload

clean:
	rm -rf dist/*
	rmdir dist
	rm -rf build/*
	rmdir build
	rm -rf pdfcli.egg-info/*
	rmdir pdfcli.egg-info

coverage:
	coverage run tests.py

coverage_report:
	coverage report -m

coverage_report_html:
	coverage html -d coverage_html

coverage_show_html:
	open coverage_html/index.html
