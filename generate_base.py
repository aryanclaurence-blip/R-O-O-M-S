import os
import textwrap

repo_dir = r"d:\ANTIGRAVITY\ROOMS"

folders = [
    ".github",
    "docs",
    "examples",
    "resources",
    "icons",
    "tests/unit/core",
    "tests/integration/revit",
    "sample_models",
    "scripts",
    "RoomDimensionManager.extension",
    "RoomDimensionManager.extension/hooks",
    "RoomDimensionManager.extension/Room Dimension.tab",
    "RoomDimensionManager.extension/Room Dimension.tab/QA.panel",
    "RoomDimensionManager.extension/Room Dimension.tab/QA.panel/SetDimensions.pushbutton",
    "RoomDimensionManager.extension/Room Dimension.tab/QA.panel/CrossCheck.pushbutton",
    "RoomDimensionManager.extension/Room Dimension.tab/Settings.panel",
    "RoomDimensionManager.extension/Room Dimension.tab/Settings.panel/Settings.pushbutton",
    "RoomDimensionManager.extension/Room Dimension.tab/Reports.panel",
    "RoomDimensionManager.extension/Room Dimension.tab/Reports.panel/Reports.pushbutton",
    "RoomDimensionManager.extension/Room Dimension.tab/Diagnostics.panel",
    "RoomDimensionManager.extension/Room Dimension.tab/Diagnostics.panel/Diagnostics.pushbutton",
    "RoomDimensionManager.extension/Room Dimension.tab/Help.panel",
    "RoomDimensionManager.extension/Room Dimension.tab/Help.panel/About.pushbutton",
    "RoomDimensionManager.extension/Room Dimension.tab/Help.panel/Help.pushbutton",
    "RoomDimensionManager.extension/lib/rdm",
    "RoomDimensionManager.extension/lib/rdm/core",
    "RoomDimensionManager.extension/lib/rdm/revit",
    "RoomDimensionManager.extension/lib/rdm/ui",
    "RoomDimensionManager.extension/lib/rdm/app",
    "RoomDimensionManager.extension/lib/rdm/utils",
    "RoomDimensionManager.extension/lib/rdm/models",
    "RoomDimensionManager.extension/lib/rdm/interfaces",
    "RoomDimensionManager.extension/lib/rdm/exceptions"
]

files = {}

files[".gitignore"] = """
# Python
__pycache__/
*.py[cod]
*$py.class

# Revit/pyRevit
*.log
debug_log.txt
*.rvt.backup
*.rfa.backup

# Config
.env
local_settings.ini
"""

files[".editorconfig"] = """
root = true

[*]
charset = utf-8
end_of_line = crlf
indent_style = space
indent_size = 4
trim_trailing_whitespace = true
insert_final_newline = true

[*.md]
trim_trailing_whitespace = false
"""

files["README.md"] = """
# Room Dimension Manager

Enterprise-grade pyRevit extension for automatically calculating and cross-checking room dimensions based on mathematically precise polygon boundaries.

## Features
- **Set Dimensions:** Automatically inject calculated Length/Width into Room parameters.
- **Cross Check:** Compare model geometry against existing parameter values.
- **Reporting:** Export QA results to CSV.

## Compatibility
- Autodesk Revit 2024, 2025, 2026, 2027
- pyRevit (CPython3 Engine)

## Documentation
See the `docs/` folder for detailed guides.
"""

files["LICENSE"] = """
MIT License
"""

files["CHANGELOG.md"] = """
# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
- Initial repository skeleton setup.
"""

files["CONTRIBUTING.md"] = """
# Contributing Guidelines

1. Fork the repository.
2. Create a feature branch from `main`.
3. Ensure all tests pass.
4. Adhere to PEP8 coding standards.
5. Submit a Pull Request.
"""

files["CODEOWNERS"] = """
* @aryanclaurence-blip
"""

files["pyproject.toml"] = """
[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q"
testpaths = [
    "tests",
]

[tool.black]
line-length = 100
"""

files["RoomDimensionManager.extension/extension.json"] = """
{
  "name": "Room Dimension Manager",
  "description": "Enterprise-grade room dimension QA tool.",
  "author": "aryanclaurence",
  "version": "1.0.0",
  "url": "https://github.com/aryanclaurence-blip/R-O-O-M-S"
}
"""

files["docs/DeveloperGuide.md"] = """
# Developer Guide
Details on local setup, tests, and dependency injection patterns.
"""
files["docs/ArchitectureGuide.md"] = """
# Architecture Guide
System design and boundary contexts.
"""
files["docs/UserGuide.md"] = """
# User Guide
How to operate the extension.
"""
files["docs/API.md"] = """
# API Guide
Internal interfaces and models.
"""

# Base Pushbutton Bundle & Script
base_script = """
# -*- coding: utf-8 -*-
\"\"\"
{description}
\"\"\"
import sys
import os
import logging
from typing import Any

# Configure simple fallback logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main() -> None:
    \"\"\"Primary execution entry point for the command.\"\"\"
    try:
        logger.info("Starting command: {command_name}")
        # TODO: Instantiate controllers from lib.rdm and execute
        pass
    except Exception as e:
        logger.error(f"Critical error executing command: {{e}}")
    finally:
        logger.info("Command {command_name} terminated safely.")

if __name__ == '__main__':
    main()
"""

pushbuttons = {
    "SetDimensions": ("Set Room Dimensions", "Calculates and writes dimensions to parameters."),
    "CrossCheck": ("Cross Check", "QA tool to compare geometry vs parameters."),
    "Settings": ("Settings", "Configure tolerances and target parameters."),
    "Reports": ("Export Reports", "Generates CSV reports from historical runs."),
    "Diagnostics": ("Diagnostics", "Checks model health and configuration status."),
    "About": ("About", "Information about the Room Dimension Manager."),
    "Help": ("Help", "Opens the user guide.")
}

for folder_name, (cmd_name, desc) in pushbuttons.items():
    panel_name = "QA"
    if folder_name == "Settings": panel_name = "Settings"
    elif folder_name == "Reports": panel_name = "Reports"
    elif folder_name == "Diagnostics": panel_name = "Diagnostics"
    elif folder_name in ("About", "Help"): panel_name = "Help"
    
    path = f"RoomDimensionManager.extension/Room Dimension.tab/{panel_name}.panel/{folder_name}.pushbutton"
    
    files[f"{path}/script.py"] = base_script.format(command_name=cmd_name, description=desc).lstrip()
    
    files[f"{path}/bundle.yaml"] = f"""
title: "{cmd_name}"
tooltip: "{desc}"
author: "aryanclaurence"
engine: CPython3
""".lstrip()


for folder in folders:
    os.makedirs(os.path.join(repo_dir, folder), exist_ok=True)

for rel_path, content in files.items():
    full_path = os.path.join(repo_dir, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\\n")

print("Base repository skeleton created successfully.")
