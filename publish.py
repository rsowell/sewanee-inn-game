"""Build this game and refresh the files served by GitHub Pages."""
from pathlib import Path
import shutil
import subprocess
import sys


# On localhost pygbag 0.9.3 otherwise asks its own development server
# for wheels. A static server (http.server or GitHub Pages) needs the CDN.
PACKAGE_INDEX = "https://pygame-web.github.io/cdn/"
STARTUP = "async def custom_site():\n"


def main():
    root = Path(__file__).resolve().parent
    subprocess.run(
        [sys.executable, "-m", "pygbag", "--build", "--title", "Sewanee Inn Game", "game"],
        cwd=root,
        check=True,
    )
    build = root / "game" / "build" / "web"
    files = ("index.html", "game.apk", "game.tar.gz", "favicon.png")
    for name in files:
        if not (build / name).is_file():
            raise SystemExit(f"Build output missing: {build / name}")

    html = (build / "index.html").read_text(encoding="utf-8")
    if html.count(STARTUP) != 1:
        raise SystemExit("Unexpected pygbag startup code. Check the pinned pygbag version.")
    html = html.replace(
        STARTUP,
        STARTUP + f'    import os\n    os.environ["PYGPI"] = {PACKAGE_INDEX!r}\n',
        1,
    )

    docs = root / "docs"
    docs.mkdir(exist_ok=True)
    for name in files:
        if name != "index.html":
            shutil.copy2(build / name, docs / name)
    (docs / "index.html").write_text(html, encoding="utf-8")
    (docs / ".nojekyll").touch()
    print("Updated docs/ for GitHub Pages.")


if __name__ == "__main__":
    main()
