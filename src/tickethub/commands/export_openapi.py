import json
from pathlib import Path

from tickethub.main import app

DOCS_DIR = Path("docs")
OPENAPI_PATH = DOCS_DIR / "openapi.json"
REDOC_PATH = DOCS_DIR / "redoc.html"


def main() -> None:
    # Generira statičku OpenAPI dokumentaciju
    DOCS_DIR.mkdir(exist_ok=True)

    openapi_schema = app.openapi()

    OPENAPI_PATH.write_text(
        json.dumps(openapi_schema, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    redoc_html = """<!DOCTYPE html>
<html lang="hr">
<head>
  <meta charset="UTF-8">
  <title>TicketHub API dokumentacija</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body {
      margin: 0;
      padding: 0;
    }
  </style>
</head>
<body>
  <redoc spec-url="openapi.json"></redoc>
  <script src="https://cdn.jsdelivr.net/npm/redoc@2/bundles/redoc.standalone.js"></script>
</body>
</html>
"""

    REDOC_PATH.write_text(redoc_html, encoding="utf-8")

    print(f"Generirano: {OPENAPI_PATH}")
    print(f"Generirano: {REDOC_PATH}")


if __name__ == "__main__":
    main()