$ErrorActionPreference = 'Stop'
$repoDir = 'd:\ANTIGRAVITY\ROOMS'

$folders = @(
    ".github",
    "docs",
    "examples",
    "resources",
    "icons",
    "tests\unit\core",
    "tests\integration\revit",
    "sample_models",
    "scripts",
    "RoomDimensionManager.extension",
    "RoomDimensionManager.extension\hooks",
    "RoomDimensionManager.extension\Room Dimension.tab",
    "RoomDimensionManager.extension\Room Dimension.tab\QA.panel",
    "RoomDimensionManager.extension\Room Dimension.tab\QA.panel\SetDimensions.pushbutton",
    "RoomDimensionManager.extension\Room Dimension.tab\QA.panel\CrossCheck.pushbutton",
    "RoomDimensionManager.extension\Room Dimension.tab\Settings.panel",
    "RoomDimensionManager.extension\Room Dimension.tab\Settings.panel\Settings.pushbutton",
    "RoomDimensionManager.extension\Room Dimension.tab\Reports.panel",
    "RoomDimensionManager.extension\Room Dimension.tab\Reports.panel\Reports.pushbutton",
    "RoomDimensionManager.extension\Room Dimension.tab\Diagnostics.panel",
    "RoomDimensionManager.extension\Room Dimension.tab\Diagnostics.panel\Diagnostics.pushbutton",
    "RoomDimensionManager.extension\Room Dimension.tab\Help.panel",
    "RoomDimensionManager.extension\Room Dimension.tab\Help.panel\About.pushbutton",
    "RoomDimensionManager.extension\Room Dimension.tab\Help.panel\Help.pushbutton",
    "RoomDimensionManager.extension\lib\rdm",
    "RoomDimensionManager.extension\lib\rdm\core",
    "RoomDimensionManager.extension\lib\rdm\revit",
    "RoomDimensionManager.extension\lib\rdm\ui",
    "RoomDimensionManager.extension\lib\rdm\ui\views",
    "RoomDimensionManager.extension\lib\rdm\ui\viewmodels",
    "RoomDimensionManager.extension\lib\rdm\app",
    "RoomDimensionManager.extension\lib\rdm\utils",
    "RoomDimensionManager.extension\lib\rdm\models",
    "RoomDimensionManager.extension\lib\rdm\interfaces",
    "RoomDimensionManager.extension\lib\rdm\exceptions",
    "RoomDimensionManager.extension\lib\rdm\graphics",
    "RoomDimensionManager.extension\lib\rdm\classification",
    "RoomDimensionManager.extension\lib\rdm\calculation",
    "RoomDimensionManager.extension\lib\rdm\geometry",
    "RoomDimensionManager.extension\lib\rdm\parameters",
    "RoomDimensionManager.extension\lib\rdm\transactions",
    "RoomDimensionManager.extension\lib\rdm\logging",
    "RoomDimensionManager.extension\lib\rdm\configuration",
    "RoomDimensionManager.extension\lib\rdm\services",
    "RoomDimensionManager.extension\lib\rdm\repositories",
    "RoomDimensionManager.extension\lib\rdm\validation",
    "RoomDimensionManager.extension\lib\rdm\factories",
    "RoomDimensionManager.extension\lib\rdm\commands",
    "RoomDimensionManager.extension\lib\rdm\reports"
)

foreach ($f in $folders) {
    $path = Join-Path $repoDir $f
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
    }
}

$files = @{}

$files['.gitignore'] = @"
__pycache__/
*.py[cod]
*$py.class
*.log
debug_log.txt
*.rvt.backup
*.rfa.backup
.env
local_settings.ini
"@

$files['.editorconfig'] = @"
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
"@

$files['README.md'] = @"
# Room Dimension Manager
Enterprise-grade pyRevit extension for automatically calculating and cross-checking room dimensions.
"@

$files['LICENSE'] = "MIT License"
$files['CHANGELOG.md'] = "# Changelog`n## [Unreleased]`n- Initial skeleton."
$files['CONTRIBUTING.md'] = "# Contributing Guidelines`n1. Fork the repo."
$files['CODEOWNERS'] = "* @aryanclaurence-blip"

$files['pyproject.toml'] = @"
[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q"
testpaths = ["tests"]
[tool.black]
line-length = 100
"@

$files['RoomDimensionManager.extension\extension.json'] = @"
{
  "name": "Room Dimension Manager",
  "description": "Enterprise-grade room dimension QA tool.",
  "author": "aryanclaurence",
  "version": "1.0.0",
  "url": "https://github.com/aryanclaurence-blip/R-O-O-M-S"
}
"@

$files['docs\DeveloperGuide.md'] = "# Developer Guide"
$files['docs\ArchitectureGuide.md'] = "# Architecture Guide"
$files['docs\UserGuide.md'] = "# User Guide"
$files['docs\API.md'] = "# API Guide"
$files['docs\InstallationGuide.md'] = "# Installation Guide"
$files['docs\TroubleshootingGuide.md'] = "# Troubleshooting Guide"
$files['docs\ReleaseGuide.md'] = "# Release Guide"

$baseScript = @"
# -*- coding: utf-8 -*-
`"`"`"
{0}
`"`"`"
import sys
import os
import logging
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main() -> None:
    `"`"`"Primary execution entry point.`"`"`"
    try:
        logger.info("Starting command: {1}")
        pass
    except Exception as e:
        logger.error(f"Critical error: {e}")
    finally:
        logger.info("Command {1} terminated.")

if __name__ == '__main__':
    main()
"@

$pushbuttons = @{
    "QA.panel\SetDimensions.pushbutton" = @("Set Room Dimensions", "Set Dimensions")
    "QA.panel\CrossCheck.pushbutton" = @("Cross Check", "Cross Check")
    "Settings.panel\Settings.pushbutton" = @("Settings", "Settings")
    "Reports.panel\Reports.pushbutton" = @("Export Reports", "Reports")
    "Diagnostics.panel\Diagnostics.pushbutton" = @("Diagnostics", "Diagnostics")
    "Help.panel\About.pushbutton" = @("About", "About")
    "Help.panel\Help.pushbutton" = @("Help", "Help")
}

foreach ($key in $pushbuttons.Keys) {
    $vals = $pushbuttons[$key]
    $desc = $vals[0]
    $cmd = $vals[1]
    
    $pathScript = "RoomDimensionManager.extension\Room Dimension.tab\$key\script.py"
    $scriptContent = $baseScript.Replace('{0}', $desc).Replace('{1}', $cmd)
    $files[$pathScript] = $scriptContent
    
    $pathYaml = "RoomDimensionManager.extension\Room Dimension.tab\$key\bundle.yaml"
    $files[$pathYaml] = @"
title: "$cmd"
tooltip: "$desc"
author: "aryanclaurence"
engine: CPython3
"@
}

foreach ($key in $files.Keys) {
    $fullPath = Join-Path $repoDir $key
    $dir = Split-Path $fullPath
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    Set-Content -Path $fullPath -Value $files[$key] -Encoding UTF8
}

Write-Output "Base generation complete."
