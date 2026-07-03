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

    openapi_json = json.dumps(openapi_schema, ensure_ascii=False)
    openapi_json = openapi_json.replace("</", "<\\/")

    redoc_html = f"""<!DOCTYPE html>
<html lang="hr">
<head>
  <meta charset="UTF-8">
  <title>TicketHub API dokumentacija</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body {{
      margin: 0;
      padding: 0;
    }}
  </style>
</head>
<body>
  <redoc id="redoc-container"></redoc>

  <script>
    window.__OPENAPI_SPEC__ = {openapi_json};
  </script>
  <script src="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"></script>
  <script>
    Redoc.init(
      window.__OPENAPI_SPEC__,
      {{}},
      document.getElementById("redoc-container")
    );
  </script>
</body>
</html>
"""

    REDOC_PATH.write_text(redoc_html, encoding="utf-8")

    print(f"Generirano: {OPENAPI_PATH}")
    print(f"Generirano: {REDOC_PATH}")


if __name__ == "__main__":
    main()
