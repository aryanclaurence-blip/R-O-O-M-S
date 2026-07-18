# Room Dimension Manager - Enterprise Edition

Welcome to the **Room Dimension Manager**, an enterprise-grade Autodesk Revit application built on the pyRevit framework. 

This application provides robust, automated extraction, classification, calculation, and QA verification of engineering room dimensions (Length/Width) directly from Revit geometry.

## Architecture

The Room Dimension Manager is built upon a strict **Clean Architecture / SOLID** foundation to ensure maintainability, testability, and enterprise scale.

Key Engines:
*   **Computational Geometry Engine**: Immutable extraction and analysis of normalized room geometry.
*   **Shape Classification Engine**: Mathematical identification of architectural footprints (Rectangles, L-Shapes, Polygons).
*   **Dimension Calculation Engine**: Derivation of engineering Length and Width based on classified geometry strategies.
*   **Parameter Management Engine**: Bidirectional parameter interaction and tolerance-based QA cross-checking.
*   **Reporting & Export Engine**: High-performance serialization of analysis results into CSV/JSON/Markdown.
*   **Transaction & Graphics Override Engine**: Exception-safe Revit database transactions and view-specific QA visualizations.

## Features

1.  **Set Room Dimensions**: Automatically calculates and writes dimensions for thousands of rooms concurrently.
2.  **Cross Check Dimensions**: Non-destructive auditing of existing parameters against live geometric calculations.
3.  **Visual Diagnostics**: Instantly identifies discrepancies using view-specific color overrides (Pass/Fail/Warning).
4.  **Extensive Reporting**: Exports deep statistical breakdowns for project QA documentation.

## Requirements

*   Autodesk Revit 2024 / 2025 / 2026 / 2027
*   pyRevit (Latest version)
*   Windows 10 / 11

## Documentation

*   [Installation Guide](INSTALL.md)
*   [User Guide](USER_GUIDE.md)
*   [Developer Guide](DEVELOPER_GUIDE.md)
*   [Architecture Overview](ARCHITECTURE.md)
*   [API Reference](API_REFERENCE.md)
