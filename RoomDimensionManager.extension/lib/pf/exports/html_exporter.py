# -*- coding: utf-8 -*-
"""HTML Exporter for PARAMS FLOW execution reports."""
import time

def export_pf_html(filepath, results, summary, doc_title="Revit Model"):
    html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"/>
    <title>PARAMS FLOW Execution Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; color: #333; }}
        h1 {{ color: #0078D7; border-bottom: 2px solid #0078D7; padding-bottom: 8px; }}
        .summary-box {{ background: #F0F0F0; border: 1px solid #D9D9D9; padding: 12px; margin-bottom: 20px; border-radius: 4px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 16px; }}
        th {{ background: #0078D7; color: white; text-align: left; padding: 8px; font-size: 13px; }}
        td {{ padding: 6px 8px; border-bottom: 1px solid #EAEAEA; font-size: 12px; }}
        tr:nth-child(even) {{ background: #F9F9F9; }}
        .UPDATED {{ color: #008000; font-weight: bold; }}
        .FAILED {{ color: #E81123; font-weight: bold; }}
        .SKIPPED {{ color: #D8A41E; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>PARAMS FLOW Execution Report</h1>
    <div class="summary-box">
        <p><strong>Project:</strong> {project}</p>
        <p><strong>Date:</strong> {date}</p>
        <p><strong>Mappings Executed:</strong> {mappings_count} | <strong>Elements Processed:</strong> {processed_count}</p>
        <p><strong>Updated:</strong> {updated_count} | <strong>Skipped:</strong> {skipped_count} | <strong>Failed:</strong> {failed_count}</p>
        <p><strong>Success Rate:</strong> {success_rate:.1f}% | <strong>Elapsed Time:</strong> {elapsed:.2f}s</p>
    </div>
    <table>
        <thead>
            <tr>
                <th>Element ID</th>
                <th>Category</th>
                <th>Source Mapping</th>
                <th>Target Parameter</th>
                <th>Old Value</th>
                <th>New Value</th>
                <th>Status</th>
                <th>Message</th>
            </tr>
        </thead>
        <tbody>
""".format(
        project=doc_title,
        date=time.strftime("%Y-%m-%d %H:%M:%S"),
        mappings_count=getattr(summary, 'mappings_count', 0),
        processed_count=getattr(summary, 'processed_count', 0),
        updated_count=getattr(summary, 'updated_count', 0),
        skipped_count=getattr(summary, 'skipped_count', 0),
        failed_count=getattr(summary, 'failed_count', 0),
        success_rate=getattr(summary, 'success_rate', 100.0),
        elapsed=getattr(summary, 'elapsed_time', 0.0)
    )

    for r in results:
        html_content += """            <tr>
                <td>{eid}</td>
                <td>{cat}</td>
                <td>{src}</td>
                <td>{tgt}</td>
                <td>{old}</td>
                <td>{new}</td>
                <td class="{status}">{status}</td>
                <td>{msg}</td>
            </tr>
""".format(
            eid=getattr(r, 'ElementId', ''),
            cat=getattr(r, 'CategoryName', ''),
            src=getattr(r, 'SourceMapping', ''),
            tgt=getattr(r, 'TargetParameter', ''),
            old=getattr(r, 'OldValue', ''),
            new=getattr(r, 'NewValue', ''),
            status=getattr(r, 'Status', ''),
            msg=getattr(r, 'Message', '')
        )

    html_content += """        </tbody>
    </table>
</body>
</html>"""

    with open(filepath, 'w') as f:
        f.write(html_content)
