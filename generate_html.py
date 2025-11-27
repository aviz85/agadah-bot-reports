#!/usr/bin/env python3
"""
Generate HTML reports from E2E test markdown files.
Creates a beautiful RTL Hebrew website with individual test reports.
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
import markdown

# Source batch folder
BATCH_DIR = Path(__file__).parent.parent / "batch_20251127_013755"
OUTPUT_DIR = Path(__file__).parent

# Hebrew translations for test names
TEST_NAMES_HEB = {
    "Chanukah_Light_Miracle": "חנוכה - נס האור",
    "Honesty_Truth_Teen": "אמת ויושר לנוער",
    "Talmud_Wisdom_Stories": "סיפורי חכמה מהתלמוד",
    "Environment_Jewish_View": "איכות הסביבה - מבט יהודי",
    "Teamwork_Games": "משחקי עבודת צוות",
    "Purim_Hidden_Revealed": "פורים - הנסתר והנגלה",
    "Sukkot_Joy_Hospitality": "סוכות - שמחה והכנסת אורחים",
    "Kibud_Av_VaEm": "כיבוד אב ואם",
    "Jewish_Heroes_Stories": "סיפורי גבורה יהודית",
    "Leadership_Challenge": "אתגר מנהיגות"
}

# Activity type translations
ACTIVITY_TYPES_HEB = {
    "religious_holiday": "חג דתי",
    "values_education": "חינוך ערכי",
    "story_session": "מפגש סיפורים",
    "discussion": "דיון",
    "game_based": "משחקים",
    "combined": "משולב"
}

# Age group translations
AGE_GROUPS_HEB = {
    "middle": "בינוני (10-13)",
    "teen": "נוער (14-16)"
}

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link href="https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #2563eb;
            --primary-dark: #1d4ed8;
            --secondary: #64748b;
            --success: #22c55e;
            --danger: #ef4444;
            --warning: #f59e0b;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text: #1e293b;
            --text-muted: #64748b;
            --border: #e2e8f0;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Heebo', sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.7;
            direction: rtl;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        header {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            color: white;
            padding: 3rem 2rem;
            margin-bottom: 2rem;
            border-radius: 0 0 2rem 2rem;
            box-shadow: 0 4px 20px rgba(37, 99, 235, 0.3);
        }}
        
        header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }}
        
        header p {{
            opacity: 0.9;
            font-size: 1.1rem;
        }}
        
        .breadcrumb {{
            margin-bottom: 1.5rem;
        }}
        
        .breadcrumb a {{
            color: var(--primary);
            text-decoration: none;
            font-weight: 500;
        }}
        
        .breadcrumb a:hover {{
            text-decoration: underline;
        }}
        
        .card {{
            background: var(--card-bg);
            border-radius: 1rem;
            padding: 2rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            border: 1px solid var(--border);
        }}
        
        .card h2 {{
            color: var(--primary);
            font-size: 1.5rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--border);
        }}
        
        .card h3 {{
            color: var(--text);
            font-size: 1.2rem;
            margin: 1.5rem 0 0.75rem;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        
        .stat-card {{
            background: var(--card-bg);
            border-radius: 1rem;
            padding: 1.5rem;
            text-align: center;
            border: 1px solid var(--border);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        
        .stat-value {{
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary);
        }}
        
        .stat-label {{
            color: var(--text-muted);
            font-size: 0.9rem;
            margin-top: 0.25rem;
        }}
        
        .test-list {{
            display: grid;
            gap: 1rem;
        }}
        
        .test-item {{
            display: flex;
            align-items: center;
            padding: 1.25rem;
            background: var(--card-bg);
            border-radius: 0.75rem;
            border: 1px solid var(--border);
            text-decoration: none;
            color: var(--text);
            transition: all 0.2s;
        }}
        
        .test-item:hover {{
            border-color: var(--primary);
            box-shadow: 0 4px 15px rgba(37, 99, 235, 0.15);
            transform: translateX(-4px);
        }}
        
        .test-status {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-left: 1rem;
            font-size: 1.25rem;
        }}
        
        .test-status.pass {{
            background: #dcfce7;
            color: var(--success);
        }}
        
        .test-status.fail {{
            background: #fee2e2;
            color: var(--danger);
        }}
        
        .test-info {{
            flex: 1;
        }}
        
        .test-name {{
            font-weight: 600;
            font-size: 1.1rem;
            margin-bottom: 0.25rem;
        }}
        
        .test-meta {{
            color: var(--text-muted);
            font-size: 0.85rem;
        }}
        
        .test-duration {{
            color: var(--secondary);
            font-weight: 500;
        }}
        
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 500;
            margin-left: 0.5rem;
        }}
        
        .badge-primary {{
            background: #dbeafe;
            color: var(--primary);
        }}
        
        .badge-success {{
            background: #dcfce7;
            color: var(--success);
        }}
        
        .badge-danger {{
            background: #fee2e2;
            color: var(--danger);
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }}
        
        th, td {{
            padding: 0.75rem 1rem;
            text-align: right;
            border-bottom: 1px solid var(--border);
        }}
        
        th {{
            background: var(--bg);
            font-weight: 600;
            color: var(--text-muted);
        }}
        
        tr:hover {{
            background: var(--bg);
        }}
        
        .content-section {{
            margin: 1.5rem 0;
            padding: 1.5rem;
            background: var(--bg);
            border-radius: 0.75rem;
            border-right: 4px solid var(--primary);
        }}
        
        .content-section h4 {{
            color: var(--primary);
            margin-bottom: 0.75rem;
        }}
        
        pre {{
            background: #1e293b;
            color: #e2e8f0;
            padding: 1rem;
            border-radius: 0.5rem;
            overflow-x: auto;
            direction: ltr;
            text-align: left;
            font-size: 0.85rem;
            line-height: 1.5;
        }}
        
        code {{
            font-family: 'Fira Code', monospace;
        }}
        
        .activity-content {{
            line-height: 1.8;
        }}
        
        .activity-content h1, .activity-content h2, .activity-content h3 {{
            color: var(--primary);
            margin: 1.5rem 0 1rem;
        }}
        
        .activity-content ul, .activity-content ol {{
            margin: 1rem 0;
            padding-right: 2rem;
        }}
        
        .activity-content li {{
            margin: 0.5rem 0;
        }}
        
        .activity-content blockquote {{
            border-right: 4px solid var(--primary);
            padding: 1rem 1.5rem;
            margin: 1rem 0;
            background: var(--bg);
            border-radius: 0 0.5rem 0.5rem 0;
            font-style: italic;
        }}
        
        .activity-content hr {{
            border: none;
            border-top: 2px solid var(--border);
            margin: 2rem 0;
        }}
        
        footer {{
            text-align: center;
            padding: 2rem;
            color: var(--text-muted);
            border-top: 1px solid var(--border);
            margin-top: 3rem;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 1rem;
            }}
            
            header {{
                padding: 2rem 1rem;
            }}
            
            header h1 {{
                font-size: 1.75rem;
            }}
            
            .stats-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
    </style>
</head>
<body>
    {content}
    <footer>
        <p>נוצר על ידי Agadah-Bot | מודל: Claude Opus 4.5 | {date}</p>
    </footer>
</body>
</html>
'''

def extract_test_info(md_content: str) -> dict:
    """Extract test information from markdown content."""
    info = {}
    
    # Extract test name from title
    title_match = re.search(r'# E2E Test Report: (\w+)', md_content)
    if title_match:
        info['name'] = title_match.group(1)
        info['name_heb'] = TEST_NAMES_HEB.get(info['name'], info['name'])
    
    # Extract configuration
    config_match = re.search(r'\| model \| (.+?) \|', md_content)
    if config_match:
        info['model'] = config_match.group(1)
    
    # Extract user request
    request_match = re.search(r'\*\*User Request:\*\* (.+)', md_content)
    if request_match:
        info['user_request'] = request_match.group(1)
    
    # Extract activity details JSON
    json_match = re.search(r'```json\n({[\s\S]*?})\n```', md_content)
    if json_match:
        try:
            info['activity_details'] = json.loads(json_match.group(1))
        except:
            pass
    
    # Extract final output (the activity plan)
    # The final output is wrapped in ```markdown ... ``` code block
    final_output_match = re.search(r'## Final Output\n\n```markdown\n([\s\S]+?)```', md_content)
    if final_output_match:
        info['final_output'] = final_output_match.group(1).strip()
    else:
        # Fallback: try without code block wrapper
        final_output_match = re.search(r'## Final Output\n\n([\s\S]+?)(?=\n## |$)', md_content)
        if final_output_match:
            info['final_output'] = final_output_match.group(1).strip()
    
    # Extract step timings
    steps = []
    step_pattern = r'STEP: (.+?)\n.*?Duration: ([\d.]+)s.*?Result: (\w+)'
    for match in re.finditer(step_pattern, md_content, re.DOTALL):
        steps.append({
            'name': match.group(1),
            'duration': float(match.group(2)),
            'status': match.group(3)
        })
    info['steps'] = steps
    
    # Calculate total duration
    info['total_duration'] = sum(s['duration'] for s in steps) if steps else 0
    
    return info


def generate_index_html(tests: list) -> str:
    """Generate the main index page."""
    # Calculate stats
    total = len(tests)
    passed = sum(1 for t in tests if t.get('status') == 'PASS')
    failed = total - passed
    total_time = sum(t.get('total_duration', 0) for t in tests)
    
    stats_html = f'''
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value">{total}</div>
            <div class="stat-label">סה"כ בדיקות</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" style="color: var(--success)">{passed}</div>
            <div class="stat-label">עברו בהצלחה</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" style="color: var(--danger)">{failed}</div>
            <div class="stat-label">נכשלו</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{total_time/60:.1f}</div>
            <div class="stat-label">דקות סה"כ</div>
        </div>
    </div>
    '''
    
    # Generate test list
    tests_html = '<div class="test-list">'
    for test in tests:
        status_class = 'pass' if test.get('status') == 'PASS' else 'fail'
        status_icon = '✓' if test.get('status') == 'PASS' else '✗'
        
        activity_type = test.get('activity_details', {}).get('activity_type', '')
        activity_type_heb = ACTIVITY_TYPES_HEB.get(activity_type, activity_type)
        
        age_group = test.get('activity_details', {}).get('age_group', '')
        age_group_heb = AGE_GROUPS_HEB.get(age_group, age_group)
        
        duration_min = test.get('activity_details', {}).get('duration_minutes', 0)
        
        tests_html += f'''
        <a href="{test['filename']}.html" class="test-item">
            <div class="test-status {status_class}">{status_icon}</div>
            <div class="test-info">
                <div class="test-name">{test.get('name_heb', test.get('name', 'Unknown'))}</div>
                <div class="test-meta">
                    <span class="badge badge-primary">{activity_type_heb}</span>
                    <span class="badge badge-primary">{age_group_heb}</span>
                    <span class="badge badge-primary">{duration_min} דקות</span>
                </div>
            </div>
            <div class="test-duration">{test.get('total_duration', 0)/60:.1f} דק'</div>
        </a>
        '''
    tests_html += '</div>'
    
    content = f'''
    <header>
        <div class="container">
            <h1>🕎 דוחות בדיקות Agadah-Bot</h1>
            <p>בדיקות קצה-לקצה ליצירת פעילויות חינוכיות | Claude Opus 4.5</p>
        </div>
    </header>
    <div class="container">
        <div class="card">
            <h2>📊 סיכום כללי</h2>
            {stats_html}
        </div>
        
        <div class="card">
            <h2>📋 רשימת בדיקות</h2>
            {tests_html}
        </div>
    </div>
    '''
    
    return HTML_TEMPLATE.format(
        title="דוחות בדיקות Agadah-Bot",
        content=content,
        date=datetime.now().strftime("%d/%m/%Y")
    )


def generate_test_html(test: dict, md_content: str) -> str:
    """Generate individual test report page."""
    
    # Convert markdown final output to HTML
    final_output = test.get('final_output', '')
    if final_output:
        try:
            final_output_html = markdown.markdown(final_output, extensions=['tables', 'fenced_code'])
        except:
            final_output_html = f'<pre>{final_output}</pre>'
    else:
        final_output_html = '<p>לא נמצא פלט סופי</p>'
    
    # Build steps table
    steps_html = '''
    <table>
        <thead>
            <tr>
                <th>שלב</th>
                <th>משך (שניות)</th>
                <th>סטטוס</th>
            </tr>
        </thead>
        <tbody>
    '''
    for step in test.get('steps', []):
        status_badge = 'badge-success' if step['status'] == 'SUCCESS' else 'badge-danger'
        status_text = 'הצלחה' if step['status'] == 'SUCCESS' else 'כשלון'
        steps_html += f'''
            <tr>
                <td>{step['name']}</td>
                <td>{step['duration']:.1f}</td>
                <td><span class="badge {status_badge}">{status_text}</span></td>
            </tr>
        '''
    steps_html += '</tbody></table>'
    
    # Activity details
    activity_details = test.get('activity_details', {})
    activity_type_heb = ACTIVITY_TYPES_HEB.get(activity_details.get('activity_type', ''), '')
    age_group_heb = AGE_GROUPS_HEB.get(activity_details.get('age_group', ''), '')
    
    content = f'''
    <header>
        <div class="container">
            <h1>{test.get('name_heb', test.get('name', 'Unknown'))}</h1>
            <p>{test.get('user_request', '')}</p>
        </div>
    </header>
    <div class="container">
        <div class="breadcrumb">
            <a href="index.html">← חזרה לרשימת הבדיקות</a>
        </div>
        
        <div class="card">
            <h2>📋 פרטי הפעילות</h2>
            <table>
                <tr><th>סוג פעילות</th><td>{activity_type_heb}</td></tr>
                <tr><th>קבוצת גיל</th><td>{age_group_heb}</td></tr>
                <tr><th>משך</th><td>{activity_details.get('duration_minutes', 0)} דקות</td></tr>
                <tr><th>נושא מרכזי</th><td>{activity_details.get('main_topic', '')}</td></tr>
                <tr><th>ערכים</th><td>{', '.join(activity_details.get('main_values', []))}</td></tr>
                <tr><th>מסר סיום</th><td>{activity_details.get('closing_message_theme', '')}</td></tr>
            </table>
        </div>
        
        <div class="card">
            <h2>⏱️ שלבי הביצוע</h2>
            {steps_html}
            <p style="margin-top: 1rem; color: var(--text-muted);">
                <strong>סה"כ זמן ביצוע:</strong> {test.get('total_duration', 0)/60:.1f} דקות
            </p>
        </div>
        
        <div class="card">
            <h2>📄 תוכנית הפעילות</h2>
            <div class="activity-content">
                {final_output_html}
            </div>
        </div>
    </div>
    '''
    
    return HTML_TEMPLATE.format(
        title=test.get('name_heb', test.get('name', 'Unknown')),
        content=content,
        date=datetime.now().strftime("%d/%m/%Y")
    )


def main():
    """Main function to generate all HTML reports."""
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Find all test markdown files
    test_files = sorted(BATCH_DIR.glob("test_*.md"))
    
    tests = []
    for test_file in test_files:
        print(f"Processing: {test_file.name}")
        md_content = test_file.read_text(encoding='utf-8')
        
        # Extract test info
        test_info = extract_test_info(md_content)
        test_info['filename'] = test_file.stem
        
        # Determine status from file size (small files = failed)
        test_info['status'] = 'PASS' if len(md_content) > 10000 else 'FAIL'
        
        tests.append(test_info)
        
        # Generate individual test HTML
        test_html = generate_test_html(test_info, md_content)
        output_file = OUTPUT_DIR / f"{test_file.stem}.html"
        output_file.write_text(test_html, encoding='utf-8')
        print(f"  Created: {output_file.name}")
    
    # Generate index page
    index_html = generate_index_html(tests)
    index_file = OUTPUT_DIR / "index.html"
    index_file.write_text(index_html, encoding='utf-8')
    print(f"\nCreated index: {index_file.name}")
    
    print(f"\n✅ Generated {len(tests)} test reports + index page")
    print(f"📁 Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

