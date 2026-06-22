with open("app/automl/router.py", "r", encoding="utf-8") as f:
    content = f.read()

if "is_integer_dtype" in content:
    print("Already fixed - no changes needed")
else:
    old_line = "    if total_rows > 0 and series.nunique() / total_rows > 0.9:\n"
    new_lines = "    if not pd.api.types.is_integer_dtype(series):\n        return False\n    if total_rows > 0 and series.nunique() / total_rows > 0.9:\n"

    if old_line not in content:
        print("OLD LINE NOT FOUND - manual check needed")
    else:
        content = content.replace(old_line, new_lines, 1)
        if "import pandas as pd" not in content.split("def _is_identifier_column")[0]:
            content = content.replace(
                "import logging\nimport re\n",
                "import logging\nimport re\nimport pandas as pd\n",
                1
            )
        with open("app/automl/router.py", "w", encoding="utf-8") as f:
            f.write(content)
        print("Fix applied successfully")
