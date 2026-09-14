"""Build the single-file SvelteKit UI before PlatformIO scans C++ dependencies."""
from hashlib import sha256
from pathlib import Path
import shutil
import subprocess

Import("env")

if not env.IsCleanTarget():
    project = Path(env.subst("$PROJECT_DIR"))
    web = project / "web"
    npm = shutil.which("npm")
    if npm is None:
        raise RuntimeError("Building the UI requires Node.js 22.12+ and npm on PATH")

    # Install locked dependencies on the first build and after changes to the dependency manifests.
    digest = sha256((web / "package.json").read_bytes() + (web / "package-lock.json").read_bytes()).hexdigest()
    stamp = web / "node_modules" / ".platformio-dependencies"
    if not stamp.exists() or stamp.read_text() != digest:
        subprocess.run([npm, "ci"], cwd=web, check=True)
        stamp.write_text(digest)
    subprocess.run([npm, "run", "build"], cwd=web, check=True)

    html = (web / "build" / "index.html").read_text(encoding="utf-8")
    delimiter = "N64_UI"
    if f'){delimiter}"' in html:
        raise RuntimeError("HTML contains the C++ raw-string delimiter")
    header = (
        '#pragma once\n#include <Arduino.h>\n'
        '// Generated from web/build/index.html; do not edit.\n'
        f'static const char INDEX_HTML[] PROGMEM = R"{delimiter}({html}){delimiter}";\n'
    )
    generated = Path(env.subst("$BUILD_DIR")) / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    target = generated / "web_ui_generated.h"
    # Keep mtime unchanged if the content matches, so incremental C++ builds do not repeat work.
    if not target.exists() or target.read_text(encoding="utf-8") != header:
        target.write_text(header, encoding="utf-8")
    env.Append(CPPPATH=[str(generated)])
