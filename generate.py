from pathlib import Path

from packaging.requirements import Requirement

THIS_DIR = Path(__file__).parent
SRC_DIR = THIS_DIR / "src"
DIST_DIR = THIS_DIR / "dist"

overrides = {}
overrides["aiohttp"] = [("aiohttp>=3.7.4 ; python_version == '3.6'", "aiohttp 4.x requires Python 3.7+")]
overrides["click"] = [("click>=8.0.0 ; python_version == '3.6'", "click 8.1.0+ dropped Python 3.6 support")]
overrides["colorama"] = [("colorama>=0.4.3 ; python_version == '3.6'", "colorama 0.4.5< dropped Python 3.6 support")]
overrides["ipython"] = [
    (
        "ipython>7.8.0 ; python_version <= '3.7'",
        "ipython 7.17+ dropped Python 3.6 and ipython 8+ dropped Python 3.7 support",
    )
]
overrides["pytest"] = [("pytest>6.1.1 ; python_version == '3.6'", "pytest 7.1.0+ dropped Python 3.6 support")]
overrides["platformdirs"] = [("platformdirs>=2 ; python_version == '3.6'", "platformdirs 2.5.1< dropped Python 3.6 support")]
overrides["tokenize-rt"] = [("tokenize-rt>3.2.0 ; python_version == '3.6'", "tokenize-rt 4.2.1< dropped Python 3.6 support")]
overrides["tomli"] = [("tomli>=1.1.0 ; python_version == '3.6'", "tomli 2.0.0+ dropped Python 3.6 support")]


applicable_overrides = {}
for pkg, values in overrides.items():
    parsed_pkg_overrides = [(Requirement(req), reason) for req, reason in values]
    applicable_pkg_overrides = []
    for o, reason in parsed_pkg_overrides:
        if o.marker is None or o.marker.evaluate():
            applicable_pkg_overrides.append((o, reason))
    if applicable_pkg_overrides:
        applicable_overrides[pkg] = applicable_pkg_overrides

for req_file in SRC_DIR.iterdir():
    print(f"[Generating {req_file.name}]")
    final_reqs = []
    for raw_req in req_file.read_text("utf-8").splitlines():
        if raw_req.startswith("#"):
            # Skip comments.
            continue

        req = Requirement(raw_req)
        # Overrides only make sense for development requirements.
        if req.name in applicable_overrides and "dev" in req_file.name:
            for override_req, reason in applicable_overrides[req.name]:
                print(f"  Applying {override_req!r} override\n    Reason -> '{reason}'")
                final_reqs.append(str(override_req))
        else:
            final_reqs.append(raw_req)

    DIST_DIR.mkdir(exist_ok=True)
    Path(DIST_DIR, req_file.name).write_text("\n".join(final_reqs), "utf-8")
