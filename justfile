export PYTHONPATH := "./src:../fluvius/src"

test:
    pytest -x -q --log-cli-level=info --log-level=info --html=tests/logs/report.html --self-contained-html --color=yes  ./tests/test_*.py
