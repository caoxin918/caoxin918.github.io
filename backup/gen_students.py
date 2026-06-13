#!/usr/bin/env python3
"""Parse students.md and generate team section HTML for index.html"""
import re

md_path = '/Users/youyou/PycharmProjects/ScholarHome/students.md'
html_path = '/Users/youyou/PycharmProjects/ScholarHome/index.html'

with open(md_path, 'r', encoding='utf-8') as f:
    text = f.read()

# ============================================================
# Parse sections
# ============================================================

def parse_students(section_text):
    """Parse student list lines like '- 姓名，年级，方向'"""
    students = []
    for line in section_text.strip().split('\n'):
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('格式') or line.startswith('---'):
            continue
        if line.startswith('- '):
            parts = [p.strip() for p in line[2:].split('，')]
            if len(parts) >= 2:
                name = parts[0]
                grade = parts[1]
                direction = parts[2] if len(parts) >= 3 else ''
                students.append({'name': name, 'grade': grade, 'direction': direction})
    return students

def parse_honors(section_text):
    """Parse honor entries with year-grouped names."""
    honors = []
    current_honor = None
    current_entries = []

    for line in section_text.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        # Honor title: ## 名称
        if line.startswith('## '):
            if current_honor:
                honors.append({'title': current_honor, 'entries': current_entries})
            current_honor = line[3:].strip()
            current_entries = []
        elif current_honor and '：' in line:
            # 年份：名字1、名字2
            year_part, names_part = line.split('：', 1)
            year = year_part.strip()
            # Remove trailing degree tags like （研三） etc for clean display
            names = names_part.strip()
            current_entries.append({'year': year, 'names': names})

    if current_honor:
        honors.append({'title': current_honor, 'entries': current_entries})

    return honors

# Split by top-level headings
sections = {}
current_section = None
for line in text.split('\n'):
    if line.startswith('# ') and not line.startswith('## '):
        current_section = line[2:].strip()
        sections[current_section] = []
    elif current_section is not None:
        sections[current_section].append(line)

# Parse
current_students = parse_students('\n'.join(sections.get('在读学生', [])))
grad_students = parse_students('\n'.join(sections.get('已毕业学生', [])))
honor_lines = '\n'.join(sections.get('荣誉奖项', []))
honors = parse_honors(honor_lines)

print(f"在读学生: {len(current_students)} 人")
print(f"已毕业学生: {len(grad_students)} 人")
print(f"荣誉奖项: {len(honors)} 项")
for h in honors:
    total = sum(len(e['names'].replace('、', ',').split(',')) for e in h['entries'])
    print(f"  - {h['title']}: {total} 人次")

# ============================================================
# Generate HTML
# ============================================================

def gen_student_cards(students):
    html = ''
    for s in students:
        info = s['grade']
        if s['direction']:
            info += '·' + s['direction']
        html += f'                    <div class="t-card"><div class="name">{s["name"]}</div><div class="info">{info}</div></div>\n'
    return html

def gen_honor_html(honors):
    """Generate honor pills and detail panels."""
    pills_html = ''
    details_html = ''

    honor_key_map = {
        '国家奖学金': ('scholarship', '🏅'),
        '优秀硕士毕业生': ('graduate', '🎓'),
        '优秀硕士毕业论文': ('thesis', '📝'),
    }
    honor_title_map = {
        '国家奖学金': '指导学生荣获国家奖学金',
        '优秀硕士毕业生': '西北大学优秀硕士毕业生',
        '优秀硕士毕业论文': '西北大学优秀硕士毕业论文',
    }

    for h in honors:
        key_info = honor_key_map.get(h['title'], (h['title'], '🏅'))
        key = key_info[0]
        emoji = key_info[1]
        display_title = honor_title_map.get(h['title'], h['title'])

        total_count = 0
        for e in h['entries']:
            total_count += len(e['names'].replace('、', ',').split(','))

        pills_html += f'                <button data-honor="{key}">{emoji} {h["title"]} × {total_count}人次</button>\n'

        detail = f'            <div class="honor-detail" id="honor-{key}">\n'
        detail += f'                <div class="hd-title">{display_title}（{total_count}人次）</div>\n'
        for e in h['entries']:
            detail += f'                <div class="hd-year">{e["year"]}</div>\n'
            detail += f'                <div class="hd-names">{e["names"]}</div>\n'
        detail += '            </div>\n'
        details_html += detail

    return pills_html, details_html

# Generate honor section
honor_pills_html, honor_details_html = gen_honor_html(honors)

# Build complete team section
team_html = f'''    <!-- ===== Team ===== -->
    <section class="team" id="team">
        <div class="sec-inner">
            <div class="sec-header anim">
                <h2>科研团队</h2>
                <p>Lab Members · Awards</p>
            </div>
            <div class="honor-pills">
                {honor_pills_html.strip()}
            </div>
            {honor_details_html.strip()}
            <div class="team-tabs">
                <button class="active" data-t="current">在读 ({len(current_students)}人)</button>
                <button data-t="grad">已毕业 ({len(grad_students)}人)</button>
            </div>
            <div id="tab-current">
                <div class="team-grid">
                    {gen_student_cards(current_students).strip()}
                </div>
            </div>
            <div id="tab-grad" style="display:none;">
                <div class="team-grid">
                    {gen_student_cards(grad_students).strip()}
                </div>
            </div>
        </div>
    </section>'''

# ============================================================
# Replace in index.html
# ============================================================
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

start_marker = '    <!-- ===== Team ===== -->'
start_idx = html.find(start_marker)
if start_idx < 0:
    print("ERROR: Could not find team section start")
    exit(1)

remaining = html[start_idx:]
# Find the closing </section> of the team section
pos = remaining.find('</section>')
if pos < 0:
    print("ERROR: Could not find team section end")
    exit(1)

end_idx = start_idx + pos + len('</section>')
new_html = html[:start_idx] + team_html + html[end_idx:]

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(new_html)

print(f"\nDone! Updated {html_path}")
print(f"Total lines: {len(new_html.splitlines())}")
