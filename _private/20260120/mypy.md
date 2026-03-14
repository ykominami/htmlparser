--disallow-untyped-defs 

--check-untyped-defs 

--strict

--ignore-missing-imports

# type: ignore

[mypy-package_to_fix_later.*]
ignore_errors = True

 --follow-untyped-imports 
follow-untyped-imports  config file


mypy --install-types

===============================
# mypy.ini
[mypy]
disable_error_code = import-untyped

[mypy-foobar.*]
ignore_missing_imports = True

# pyproject.toml
[[tool.mypy.overrides]]
module = ["foobar.*"]
ignore_missing_imports = true

[tool.mypy]
disable_error_code = ["import-untyped"]
