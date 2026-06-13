#!/usr/bin/env python3
"""
update.py — 统一的页面更新脚本
读取 publications.md 和 students.md，重新生成对应 HTML 并更新 index.html。
无论修改哪个 md 文件，都只需要运行此脚本即可。

用法:  python3 update.py
"""
import re, sys, os

# 获取脚本所在目录 (images/) 和项目根目录 (ScholarHome/)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)

pubs_md_path = os.path.join(PROJECT_DIR, 'files', 'publications.md')
stu_md_path  = os.path.join(PROJECT_DIR, 'files', 'students.md')
html_path    = os.path.join(PROJECT_DIR, 'index.html')

# ====================================================================
#  工具函数
# ====================================================================

def replace_section(html, marker, new_section_html):
    """替换 index.html 中以 marker 开头到 </section> 结束的整段内容。"""
    start_idx = html.find(marker)
    if start_idx < 0:
        print(f"ERROR: 找不到 {marker!r}，请检查 index.html")
        sys.exit(1)
    remaining = html[start_idx:]
    pos = remaining.find('</section>')
    if pos < 0:
        print(f"ERROR: 找不到 {marker!r} 对应的 </section>")
        sys.exit(1)
    end_idx = start_idx + pos + len('</section>')
    return html[:start_idx] + new_section_html + html[end_idx:]

# ====================================================================
#  论文部分 — publications.md
# ====================================================================

def clean_authors(s):
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'\s*，\s*', ', ', s)
    s = re.sub(r'\s*,\s*', ', ', s)
    s = re.sub(r'\s*；\s*', ', ', s)
    s = re.sub(r'\s*;\s*', ', ', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip().rstrip(',').rstrip('.').rstrip('。')

def parse_papers(lines):
    entries = []
    Q = r'["\u201c\u201d]'
    for line in lines:
        line = line.strip()
        if not line or line == '| :---- |' or line.startswith('|---'):
            continue
        if line.startswith('|') and line.endswith('|'):
            line = line[1:-1].strip()

        title = authors = rest = ''

        m = re.search(r'\u201c(.+?)\u201d', line)
        if m:
            title, before, rest = m.group(1), line[:m.start()].strip(), line[m.end():].strip()
        else:
            m = re.search(r'\[' + Q + r'(.+?)' + Q + r'\]', line)
            if m:
                title, before, rest = m.group(1), line[:m.start()].strip(), line[m.end():].strip()
            else:
                m = re.search(Q + r'(.+?)' + Q, line)
                if m:
                    title, before, rest = m.group(1), line[:m.start()].strip(), line[m.end():].strip()
                else:
                    continue

        authors = clean_authors(before.rstrip('.').rstrip(','))
        title = re.sub(r'\[([^\]]*)\]\([^\)]*\)', r'\1', title).strip()

        all_urls = re.findall(r'\]\(\s*(https?://caoxin918\.github\.io/files/[^\)]*?)\s*\)', line)
        pdf_url = all_urls[0].strip() if all_urls else ''

        cm = re.search(r'CODE\s+click\s+\[HERE\]\(\s*(https?://[^\)]+?)\s*\)', line, re.I)
        code_url = cm.group(1).strip() if cm else ''

        venue = ''
        vm = re.search(r'\*\*([^*]+?)\*\*', rest)
        if vm:
            venue = vm.group(1).strip()

        year = ''
        ym = re.findall(r'\((\d{4})\)', rest)
        if ym:
            year = ym[-1]
        else:
            ym = re.search(r'[，,]\s*(\d{4})\s*$', rest)
            if ym:
                year = ym.group(1)
            else:
                ym = re.search(r'(\d{4})\s*$', rest)
                if ym:
                    year = ym.group(1)

        links_html = ''
        if pdf_url:
            links_html += f'<a href="{pdf_url}" target="_blank">PDF</a>'
        if code_url:
            links_html += f'<a href="{code_url}" target="_blank">Code</a>'

        entries.append({'title': title, 'authors': authors, 'venue': venue,
                        'links': links_html, 'year': year})
    return entries

def parse_patents(lines):
    entries = []
    for line in lines:
        line = line.strip()
        if not line or line == '| :---- |' or line.startswith('|---'):
            continue
        if line.startswith('|') and line.endswith('|'):
            line = line[1:-1].strip()
        parts = re.split(r'。', line)
        if len(parts) < 2:
            continue
        authors = clean_authors(parts[0])
        title = parts[1].strip()
        patent_info = parts[2].strip() if len(parts) > 2 else ''
        pn = ''
        pm = re.search(r'[：:]\s*(CN\S+|ZL\S+|\d+)', patent_info)
        if pm:
            pn = pm.group(1).strip()
        status = '授权' if '授权' in patent_info else '受理'
        entries.append({'authors': authors, 'title': title, 'patent_no': pn, 'status': status})
    return entries

def parse_copyright(lines):
    entries = []
    for line in lines:
        line = line.strip()
        if not line or line == '| :---- |' or line.startswith('|---'):
            continue
        if line.startswith('|') and line.endswith('|'):
            line = line[1:-1].strip()
        parts = re.split(r'。', line)
        if len(parts) < 2:
            continue
        authors = clean_authors(parts[0])
        title = parts[1].strip()
        reg_info = parts[2].strip() if len(parts) > 2 else ''
        rn = ''
        rm = re.search(r'[：:]\s*(\S+)', reg_info)
        if rm:
            rn = rm.group(1).strip()
        entries.append({'authors': authors, 'title': title, 'reg_no': rn})
    return entries

def gen_year_grouped(entries):
    by_year = {}
    for e in entries:
        y = e.get('year', '') or '其他'
        by_year.setdefault(y, []).append(e)
    html = ''
    sorted_years = sorted(by_year.keys(), key=lambda x: (x == '其他', x), reverse=True)
    if '其他' in sorted_years:
        sorted_years.remove('其他')
        sorted_years.append('其他')
    for y in sorted_years:
        items = by_year[y]
        html += f'<div class="pub-ygroup"><div class="pub-ylabel">{y} <span style="font-size:11px;font-weight:400;color:#8095a0;">({len(items)})</span></div>\n'
        for e in items:
            html += '<div class="pe">'
            html += f'<div class="pt">{e["title"]}</div>'
            html += f'<div class="pa">{e["authors"]}</div>'
            if e['venue']:
                html += f'<div class="pv"><b>{e["venue"]}</b></div>'
            if e['links']:
                html += f'<div class="pl">{e["links"]}</div>'
            html += '</div>\n'
        html += '</div>\n'
    return html

def gen_patent_list(entries):
    html = '<div class="pub-ygroup">\n'
    for e in entries:
        badge = ''
        if e.get('status') == '授权':
            badge = ' <span style="font-size:9px;padding:1px 5px;border-radius:3px;background:#d4edda;color:#155724;margin-left:4px;">授权</span>'
        html += '<div class="pe">'
        html += f'<div class="pt">{e["title"]}{badge}</div>'
        html += f'<div class="pa">{e["authors"]}</div>'
        if e['patent_no']:
            html += f'<div class="pv">{e["patent_no"]}</div>'
        html += '</div>\n'
    html += '</div>\n'
    return html

def gen_copyright_list(entries):
    html = '<div class="pub-ygroup">\n'
    for e in entries:
        html += '<div class="pe">'
        html += f'<div class="pt">{e["title"]}</div>'
        html += f'<div class="pa">{e["authors"]}</div>'
        if e['reg_no']:
            html += f'<div class="pv">登记号: {e["reg_no"]}</div>'
        html += '</div>\n'
    html += '</div>\n'
    return html

def build_publications_section():
    with open(pubs_md_path, 'r', encoding='utf-8') as f:
        text = f.read()

    sections = re.split(r'\n(国际期刊|国际/国内会议|国内期刊|受理/授权发明专利|软件著作权)\n=+\n', text)
    cats_raw = {}
    i = 1
    while i < len(sections):
        cats_raw[sections[i].strip()] = sections[i+1].split('\n') if i+1 < len(sections) else []
        i += 2

    intl_j  = parse_papers(cats_raw.get('国际期刊', []))
    conf    = parse_papers(cats_raw.get('国际/国内会议', []))
    chn_j   = parse_papers(cats_raw.get('国内期刊', []))
    patents = parse_patents(cats_raw.get('受理/授权发明专利', []))
    copyr   = parse_copyright(cats_raw.get('软件著作权', []))

    total = len(intl_j) + len(conf) + len(chn_j) + len(patents) + len(copyr)
    print(f"[论文] 共 {total} 项：国际期刊 {len(intl_j)}，会议 {len(conf)}，国内 {len(chn_j)}，专利 {len(patents)}，软著 {len(copyr)}")

    categories = [
        ('all',    '全部',     total,         None),
        ('intl',   '国际期刊', len(intl_j),   lambda: gen_year_grouped(intl_j)),
        ('conf',   '会议论文', len(conf),     lambda: gen_year_grouped(conf)),
        ('chn',    '国内期刊', len(chn_j),    lambda: gen_year_grouped(chn_j)),
        ('patent', '发明专利', len(patents),  lambda: gen_patent_list(patents)),
        ('copy',   '软件著作', len(copyr),    lambda: gen_copyright_list(copyr)),
    ]

    tabs_html = '<div class="pub-tabs">'
    for idx, (key, label, cnt, _) in enumerate(categories):
        active = ' class="active"' if idx == 0 else ''
        tabs_html += f'<button{active} data-cat="{key}">{label}<span class="cnt">({cnt})</span></button>'
    tabs_html += '</div>'

    scroll_html = '<div class="pub-scroll">\n'
    scroll_html += '<div class="pub-cat show" data-cat="all">\n'
    cat_map = {
        'intl':   ('国际期刊', len(intl_j),  lambda: gen_year_grouped(intl_j)),
        'conf':   ('会议论文', len(conf),    lambda: gen_year_grouped(conf)),
        'chn':    ('国内期刊', len(chn_j),   lambda: gen_year_grouped(chn_j)),
        'patent': ('发明专利', len(patents), lambda: gen_patent_list(patents)),
        'copy':   ('软件著作', len(copyr),   lambda: gen_copyright_list(copyr)),
    }
    for key, (label, cnt, gen_fn) in cat_map.items():
        scroll_html += f'<div style="padding:10px 14px 2px;font-size:15px;font-weight:800;color:#1a4468;">{label} <span style="font-size:12px;font-weight:400;color:#8095a0;">({cnt})</span></div>\n'
        scroll_html += gen_fn()
    scroll_html += '</div>\n'

    for key, label, cnt, gen_fn in categories[1:]:
        scroll_html += f'<div class="pub-cat" data-cat="{key}">\n'
        scroll_html += gen_fn()
        scroll_html += '</div>\n'
    scroll_html += '</div>'

    return f'''    <!-- ===== Publications ===== -->
    <section class="publications" id="pubs">
        <div class="sec-inner">
            <div class="sec-header anim">
                <h2>科研成果</h2>
                <p>Publications &nbsp;·&nbsp; 共 {total} 项 &nbsp;·&nbsp; <a href="https://scholar.google.com/citations?hl=zh-CN&amp;user=5iI5G0IAAAAJ&amp;view_op=list_works&amp;sortby=pubdate" target="_blank" style="color:#2d6f9e;font-weight:600;">Google Scholar →</a></p>
            </div>
            {tabs_html}
            {scroll_html}
            <div class="pub-more">
                <a href="https://scholar.google.com/citations?hl=zh-CN&amp;user=5iI5G0IAAAAJ&amp;view_op=list_works&amp;sortby=pubdate" target="_blank">📚 Google Scholar 查看完整列表 →</a>
            </div>
        </div>
    </section>'''

# ====================================================================
#  学生/荣誉部分 — students.md
# ====================================================================

def parse_students(section_text):
    students = []
    for line in section_text.strip().split('\n'):
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('格式') or line.startswith('---'):
            continue
        if line.startswith('- '):
            parts = [p.strip() for p in line[2:].split('，')]
            if len(parts) >= 2:
                students.append({'name': parts[0], 'grade': parts[1],
                                 'direction': parts[2] if len(parts) >= 3 else ''})
    return students

def parse_honors(section_text):
    honors = []
    current_honor = None
    current_entries = []
    for line in section_text.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.startswith('## '):
            if current_honor:
                honors.append({'title': current_honor, 'entries': current_entries})
            current_honor = line[3:].strip()
            current_entries = []
        elif current_honor and '：' in line:
            year_part, names_part = line.split('：', 1)
            current_entries.append({'year': year_part.strip(), 'names': names_part.strip()})
    if current_honor:
        honors.append({'title': current_honor, 'entries': current_entries})
    return honors

def gen_student_cards(students):
    html = ''
    for s in students:
        info = s['grade']
        if s['direction']:
            info += '·' + s['direction']
        html += f'                    <div class="t-card"><div class="name">{s["name"]}</div><div class="info">{info}</div></div>\n'
    return html

def build_team_section():
    with open(stu_md_path, 'r', encoding='utf-8') as f:
        text = f.read()

    sections = {}
    cur = None
    for line in text.split('\n'):
        if line.startswith('# ') and not line.startswith('## '):
            cur = line[2:].strip()
            sections[cur] = []
        elif cur is not None:
            sections[cur].append(line)

    current_stu = parse_students('\n'.join(sections.get('在读学生', [])))
    grad_stu    = parse_students('\n'.join(sections.get('已毕业学生', [])))
    honors      = parse_honors('\n'.join(sections.get('荣誉奖项', [])))

    print(f"[团队] 在读 {len(current_stu)} 人，已毕业 {len(grad_stu)} 人，荣誉 {len(honors)} 项")

    honor_key_map = {
        '国家奖学金':       ('scholarship', '🏅'),
        '优秀硕士毕业生':    ('graduate',    '🎓'),
        '优秀硕士毕业论文':  ('thesis',      '📝'),
    }
    honor_title_map = {
        '国家奖学金':       '指导学生荣获国家奖学金',
        '优秀硕士毕业生':    '西北大学优秀硕士毕业生',
        '优秀硕士毕业论文':  '西北大学优秀硕士毕业论文',
    }

    pills_html = ''
    details_html = ''
    for h in honors:
        key_info = honor_key_map.get(h['title'], (h['title'], '🏅'))
        key, emoji = key_info[0], key_info[1]
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

    return f'''    <!-- ===== Team ===== -->
    <section class="team" id="team">
        <div class="sec-inner">
            <div class="sec-header anim">
                <h2>科研团队</h2>
                <p>Lab Members · Awards</p>
            </div>
            <div class="honor-pills">
                {pills_html.strip()}
            </div>
            {details_html.strip()}
            <div class="team-tabs">
                <button class="active" data-t="current">在读 ({len(current_stu)}人)</button>
                <button data-t="grad">已毕业 ({len(grad_stu)}人)</button>
            </div>
            <div id="tab-current">
                <div class="team-grid">
                    {gen_student_cards(current_stu).strip()}
                </div>
            </div>
            <div id="tab-grad" style="display:none;">
                <div class="team-grid">
                    {gen_student_cards(grad_stu).strip()}
                </div>
            </div>
        </div>
    </section>'''

# ====================================================================
#  主流程
# ====================================================================

print("=" * 50)
print("  update.py — 更新 index.html")
print("=" * 50)

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. 替换论文部分
pubs_html = build_publications_section()
html = replace_section(html, '    <!-- ===== Publications ===== -->', pubs_html)

# 2. 替换团队部分
team_html = build_team_section()
html = replace_section(html, '    <!-- ===== Team ===== -->', team_html)

# 3. 写入
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\n完成！已更新 {html_path}")
print(f"总行数: {len(html.splitlines())}")
