#!/usr/bin/env python3
"""Parse publications.md and generate complete HTML section - FIXED VERSION"""
import re

md_path = '/Users/youyou/PycharmProjects/ScholarHome/publications.md'
html_path = '/Users/youyou/PycharmProjects/ScholarHome/index.html'

with open(md_path, 'r', encoding='utf-8') as f:
    text = f.read()

def clean_authors(s):
    s = s.replace('**', '').replace('※', '').replace('†', '')
    s = re.sub(r'\s*，\s*', ', ', s)
    s = re.sub(r'\s*,\s*', ', ', s)
    s = re.sub(r'\s*；\s*', ', ', s)
    s = re.sub(r'\s*;\s*', ', ', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip().rstrip(',').rstrip('.').rstrip('。')

def parse_papers(lines):
    entries = []
    for line in lines:
        line = line.strip()
        if not line or line == '| :---- |' or line.startswith('|---'):
            continue
        if line.startswith('|') and line.endswith('|'):
            line = line[1:-1].strip()

        # Find title in quote
        title = ''
        authors = ''
        rest = ''

        # Flexible quote character class: matches ASCII ", left smart ", right smart "
        Q = r'["\u201c\u201d]'

        # Chinese smart quotes "..."
        m = re.search(r'\u201c(.+?)\u201d', line)
        if m:
            title = m.group(1)
            before = line[:m.start()].strip()
            rest = line[m.end():].strip()
        else:
            # ["title"](url) format with flexible quotes
            m = re.search(r'\[' + Q + r'(.+?)' + Q + r'\]', line)
            if m:
                title = m.group(1)
                before = line[:m.start()].strip()
                rest = line[m.end():].strip()
            else:
                # Flexible quotes "title" (any mix of ASCII/smart quotes)
                m = re.search(Q + r'(.+?)' + Q, line)
                if m:
                    title = m.group(1)
                    before = line[:m.start()].strip()
                    rest = line[m.end():].strip()
                else:
                    continue

        authors = clean_authors(before.rstrip('.').rstrip(','))
        title = re.sub(r'\[([^\]]*)\]\([^\)]*\)', r'\1', title).strip()

        # PDF link
        pdf_url = ''
        all_urls = re.findall(r'\]\(\s*(https?://caoxin918\.github\.io/files/[^\)]*?)\s*\)', line)
        if all_urls:
            pdf_url = all_urls[0].strip()

        # CODE link
        code_url = ''
        cm = re.search(r'CODE\s+click\s+\[HERE\]\(\s*(https?://[^\)]+?)\s*\)', line, re.I)
        if cm:
            code_url = cm.group(1).strip()

        # Venue
        venue = ''
        vm = re.search(r'\*\*([^*]+?)\*\*', rest)
        if vm:
            venue = vm.group(1).strip()

        # Year - try multiple patterns
        year = ''
        # Pattern 1: (YYYY)
        ym = re.findall(r'\((\d{4})\)', rest)
        if ym:
            year = ym[-1]
        else:
            # Pattern 2: ，YYYY or ,YYYY at end
            ym = re.search(r'[，,]\s*(\d{4})\s*$', rest)
            if ym:
                year = ym.group(1)
            else:
                # Pattern 3: YYYY at very end
                ym = re.search(r'(\d{4})\s*$', rest)
                if ym:
                    year = ym.group(1)

        links_html = ''
        if pdf_url:
            links_html += f'<a href="{pdf_url}" target="_blank">PDF</a>'
        if code_url:
            links_html += f'<a href="{code_url}" target="_blank">Code</a>'

        entries.append({
            'title': title,
            'authors': authors,
            'venue': venue,
            'links': links_html,
            'year': year
        })
    return entries

def parse_patents(lines):
    """Parse patents - don't use year grouping, use flat list."""
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

        # Extract patent number
        pn = ''
        pm = re.search(r'[：:]\s*(CN\S+|ZL\S+|\d+)', patent_info)
        if pm:
            pn = pm.group(1).strip()

        status = '授权' if '授权' in patent_info else '受理'

        entries.append({
            'authors': authors,
            'title': title,
            'patent_no': pn,
            'status': status,
        })
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

        entries.append({
            'authors': authors,
            'title': title,
            'reg_no': rn
        })
    return entries

# Split by sections
sections = re.split(r'\n(国际期刊|国际/国内会议|国内期刊|受理/授权发明专利|软件著作权)\n=+\n', text)

cats_raw = {}
i = 1
while i < len(sections):
    cat_name = sections[i].strip()
    content = sections[i+1] if i+1 < len(sections) else ''
    cats_raw[cat_name] = content.split('\n')
    i += 2

# Parse
intl_j = parse_papers(cats_raw.get('国际期刊', []))
conf = parse_papers(cats_raw.get('国际/国内会议', []))
chn_j = parse_papers(cats_raw.get('国内期刊', []))
patents = parse_patents(cats_raw.get('受理/授权发明专利', []))
copyright = parse_copyright(cats_raw.get('软件著作权', []))

total = len(intl_j) + len(conf) + len(chn_j) + len(patents) + len(copyright)
print(f"Total: {total}")
print(f"  国际期刊: {len(intl_j)}")
print(f"  会议论文: {len(conf)}")
print(f"  国内期刊: {len(chn_j)}")
print(f"  发明专利: {len(patents)}")
print(f"  软件著作: {len(copyright)}")

# Verify specific entries
print("\n--- 国内期刊 years ---")
for e in chn_j:
    print(f"  [{e['year']}] {e['title'][:40]}")

# === Generate HTML ===
def gen_year_grouped(entries):
    """Generate year-grouped HTML for papers/conferences."""
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
                html += f'<div class="pv">{e["venue"]}</div>'
            if e['links']:
                html += f'<div class="pl">{e["links"]}</div>'
            html += '</div>\n'
        html += '</div>\n'
    return html

def gen_patent_list(entries):
    """Generate flat patent list (no year grouping)."""
    html = '<div class="pub-ygroup">\n'
    for e in entries:
        status_badge = ''
        if e.get('status') == '授权':
            status_badge = ' <span style="font-size:9px;padding:1px 5px;border-radius:3px;background:#d4edda;color:#155724;margin-left:4px;">授权</span>'
        html += '<div class="pe">'
        html += f'<div class="pt">{e["title"]}{status_badge}</div>'
        html += f'<div class="pa">{e["authors"]}</div>'
        if e['patent_no']:
            html += f'<div class="pv">{e["patent_no"]}</div>'
        html += '</div>\n'
    html += '</div>\n'
    return html

def gen_copyright_list(entries):
    """Generate flat copyright list."""
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

# Build categories
categories = [
    ('all', '全部', total, None),
    ('intl', '国际期刊', len(intl_j), lambda: gen_year_grouped(intl_j)),
    ('conf', '会议论文', len(conf), lambda: gen_year_grouped(conf)),
    ('chn', '国内期刊', len(chn_j), lambda: gen_year_grouped(chn_j)),
    ('patent', '发明专利', len(patents), lambda: gen_patent_list(patents)),
    ('copy', '软件著作', len(copyright), lambda: gen_copyright_list(copyright)),
]

# Generate tabs
tabs_html = '<div class="pub-tabs">'
for i, (key, label, cnt, _) in enumerate(categories):
    active = ' class="active"' if i == 0 else ''
    tabs_html += f'<button{active} data-cat="{key}">{label}<span class="cnt">({cnt})</span></button>'
tabs_html += '</div>'

# Generate scrollable content
scroll_html = '<div class="pub-scroll">\n'

# ALL view
scroll_html += '<div class="pub-cat show" data-cat="all">\n'
cat_labels_map = {
    'intl': ('国际期刊', len(intl_j), lambda: gen_year_grouped(intl_j)),
    'conf': ('会议论文', len(conf), lambda: gen_year_grouped(conf)),
    'chn': ('国内期刊', len(chn_j), lambda: gen_year_grouped(chn_j)),
    'patent': ('发明专利', len(patents), lambda: gen_patent_list(patents)),
    'copy': ('软件著作', len(copyright), lambda: gen_copyright_list(copyright)),
}
for key, (label, cnt, gen_fn) in cat_labels_map.items():
    scroll_html += f'<div style="padding:10px 14px 2px;font-size:15px;font-weight:800;color:#1a4468;">{label} <span style="font-size:12px;font-weight:400;color:#8095a0;">({cnt})</span></div>\n'
    scroll_html += gen_fn()
scroll_html += '</div>\n'

# Individual category views
for key, label, cnt, gen_fn in categories[1:]:
    scroll_html += f'<div class="pub-cat" data-cat="{key}">\n'
    scroll_html += gen_fn()
    scroll_html += '</div>\n'

scroll_html += '</div>'

# Assemble complete section
section_html = f'''    <!-- ===== Publications ===== -->
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

# === Replace in index.html ===
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

start_marker = '    <!-- ===== Publications ===== -->'
start_idx = html.find(start_marker)
if start_idx < 0:
    print("ERROR: Could not find publications section start")
    exit(1)

remaining = html[start_idx:]
pos = remaining.find('</section>')
if pos < 0:
    print("ERROR: Could not find publications section end")
    exit(1)

end_idx = start_idx + pos + len('</section>')
old_section = html[start_idx:end_idx]
new_html = html[:start_idx] + section_html + html[end_idx:]

# === Update JS filter ===
new_js = '''        // Publication tabs filter
        document.querySelectorAll('.pub-tabs button').forEach(b => {
            b.addEventListener('click', () => {
                document.querySelectorAll('.pub-tabs button').forEach(x => x.classList.remove('active'));
                b.classList.add('active');
                const cat = b.dataset.cat;
                document.querySelectorAll('.pub-cat').forEach(c => {
                    c.classList.toggle('show', c.dataset.cat === cat);
                });
            });
        });'''

# Try to find and replace JS
# Look for the existing publication tabs filter or the old filter
old_js_patterns = [
    r'// Publication tabs filter\s*\n.*?}\);',
    r'// Publication filter\s*\n.*?}\);\s*\n\s*\}\);',
]
replaced = False
for pattern in old_js_patterns:
    m = re.search(pattern, new_html, re.DOTALL)
    if m:
        new_html = new_html[:m.start()] + new_js + new_html[m.end():]
        replaced = True
        print("JS filter replaced")
        break

if not replaced:
    # Just check if the new JS already exists
    if 'Publication tabs filter' in new_html:
        print("JS filter already present")
    else:
        print("WARNING: Could not find JS filter to replace")

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(new_html)

print(f"\nDone! Updated {html_path}")
print(f"Total lines: {len(new_html.splitlines())}")
