"""
export.py — SQLite → static/data.json

Run after crawling:
    python crawler.py
    python export.py
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH     = Path('data/faculty.db')
OUTPUT_PATH = Path('static/data.json')


def export():
    if not DB_PATH.exists():
        print(f'[!] Database not found: {DB_PATH}')
        print('    Run: python crawler.py')
        return

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    professors = []
    for row in conn.execute('SELECT * FROM professors ORDER BY name_kr'):
        p = dict(row)
        try:
            p['research_areas'] = json.loads(p.get('research_areas') or '[]')
        except Exception:
            p['research_areas'] = []

        papers = conn.execute(
            'SELECT * FROM papers WHERE professor_id=? ORDER BY year DESC, citations DESC',
            (p['id'],)
        ).fetchall()
        p['papers'] = [dict(paper) for paper in papers]
        professors.append(p)

    conn.close()

    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    payload = {
        'professors':    professors,
        'generated_at':  datetime.utcnow().isoformat() + 'Z',
        'total':         len(professors),
    }

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, separators=(',', ':'))

    size_kb = OUTPUT_PATH.stat().st_size / 1024
    print(f'✓  Exported {len(professors)} professors → {OUTPUT_PATH}  ({size_kb:.0f} KB)')


if __name__ == '__main__':
    export()
