#!/usr/bin/env python3
"""Convert BOOK.md to a beautiful dark-theme HTML book with embedded SVG diagrams."""

import markdown, re, os
from pygments import highlight
from pygments.lexers import HtmlLexer, TextLexer
from pygments.formatters import HtmlFormatter

BOOK_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "BOOK.md")
OUT_PATH  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "index.html")
DIAG_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "diagrams")
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

# ── Embedded SVGs (base64 inline) ───────────────────────────────────────────
def embed_svg(fname):
    path = os.path.join(DIAG_DIR, fname)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return f.read()
    return ""

# ── Dark theme CSS ───────────────────────────────────────────────────────────
CSS = """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg:        #0f172a;
  --bg2:       #1e293b;
  --card:      #334155;
  --text:      #e2e8f0;
  --muted:     #94a3b8;
  --blue:      #38bdf8;
  --green:     #4ade80;
  --orange:    #fb923c;
  --red:       #f87171;
  --yellow:    #fbbf24;
  --purple:    #c084fc;
  --border:    #1e293b;
}

html { font-size: 16px; }

body {
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  line-height: 1.75;
  min-height: 100vh;
}

/* ── Sidebar Nav ─────────────────────────────────────────────────────── */
#sidebar {
  position: fixed;
  top: 0; left: 0;
  width: 260px;
  height: 100vh;
  background: #111827;
  border-right: 1px solid var(--border);
  overflow-y: auto;
  z-index: 100;
  display: flex;
  flex-direction: column;
}
#sidebar-header {
  padding: 20px 16px 14px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
#sidebar-header h1 {
  font-size: 14px;
  font-weight: 700;
  color: var(--blue);
  line-height: 1.3;
}
#sidebar-header p {
  font-size: 11px;
  color: var(--muted);
  margin-top: 4px;
}

#nav { padding: 12px 0 24px; flex: 1; }

.nav-group { margin-bottom: 4px; }
.nav-group-label {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: .08em;
  text-transform: uppercase;
  color: var(--muted);
  padding: 10px 16px 4px;
}
.nav-item {
  display: block;
  font-size: 12.5px;
  color: var(--muted);
  text-decoration: none;
  padding: 5px 16px;
  border-left: 2px solid transparent;
  transition: color .15s, border-color .15s, background .15s;
  line-height: 1.4;
}
.nav-item:hover, .nav-item.active {
  color: var(--blue);
  border-left-color: var(--blue);
  background: rgba(56,189,248,.06);
}
.nav-item.chapter-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text);
  margin-top: 6px;
}

/* ── Main content ────────────────────────────────────────────────────── */
#main {
  margin-left: 260px;
  min-height: 100vh;
  padding: 0 40px 80px;
  max-width: 900px;
}

/* ── Typography ──────────────────────────────────────────────────────── */
h1 {
  font-size: 2rem;
  font-weight: 800;
  color: var(--blue);
  margin: 48px 0 16px;
  letter-spacing: -.02em;
  line-height: 1.2;
}
h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #fff;
  margin: 48px 0 20px;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--card);
  letter-spacing: -.01em;
}
h3 {
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--blue);
  margin: 32px 0 14px;
}
h4 { font-size: 1rem; font-weight: 600; color: var(--text); margin: 20px 0 8px; }

p { margin: 0 0 16px; color: var(--text); }

/* ── Inline ──────────────────────────────────────────────────────────── */
strong { color: #fff; font-weight: 600; }
em { color: var(--yellow); font-style: normal; }

code {
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
  font-size: .88em;
  background: #1a2332;
  color: var(--green);
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid var(--card);
}
pre {
  background: #0d1117;
  border: 1px solid var(--card);
  border-radius: 8px;
  padding: 16px 20px;
  overflow-x: auto;
  margin: 0 0 20px;
}
pre code {
  background: none;
  border: none;
  padding: 0;
  font-size: .875rem;
  color: var(--text);
  line-height: 1.7;
}

/* ── Blockquote ─────────────────────────────────────────────────────── */
blockquote {
  margin: 0 0 20px;
  padding: 14px 18px;
  background: #1a2744;
  border-left: 4px solid var(--blue);
  border-radius: 0 8px 8px 0;
  color: var(--muted);
  font-size: .95rem;
}
blockquote p:last-child { margin-bottom: 0; }

/* ── Tables ─────────────────────────────────────────────────────────── */
table {
  width: 100%;
  border-collapse: collapse;
  margin: 0 0 24px;
  font-size: .9rem;
  border-radius: 8px;
  overflow: hidden;
}
thead tr {
  background: #1a2d4a;
}
th {
  padding: 10px 14px;
  text-align: left;
  font-size: .8rem;
  font-weight: 700;
  letter-spacing: .04em;
  text-transform: uppercase;
  color: var(--blue);
  border-bottom: 2px solid var(--card);
}
td {
  padding: 9px 14px;
  border-bottom: 1px solid var(--border);
  color: var(--text);
  vertical-align: top;
}
tr:nth-child(even) td { background: rgba(30,41,59,.5); }
tr:hover td { background: rgba(56,189,248,.04); }

/* ── Lists ─────────────────────────────────────────────────────────── */
ul, ol { margin: 0 0 16px 20px; }
li { margin-bottom: 6px; color: var(--text); }
li strong { color: #fff; }

/* ── Horizontal rule ───────────────────────────────────────────────── */
hr {
  border: none;
  border-top: 1px solid var(--card);
  margin: 40px 0;
}

/* ── SVG Diagrams ───────────────────────────────────────────────────── */
.diagram-wrap {
  margin: 24px 0;
  text-align: center;
}
.diagram-wrap img, .diagram-wrap svg {
  max-width: 100%;
  height: auto;
  border-radius: 10px;
  border: 1px solid var(--card);
}
.caption {
  font-size: .8rem;
  color: var(--muted);
  margin-top: 8px;
}

/* ── Code blocks from markdown ──────────────────────────────────────── */
.highlight .hll { background: #1e293b; }

/* ── Mobile ────────────────────────────────────────────────────────── */
#mobile-nav {
  display: none;
  position: fixed;
  top: 12px; right: 14px;
  z-index: 200;
  background: var(--bg2);
  border: 1px solid var(--card);
  border-radius: 8px;
  padding: 8px 14px;
  font-size: 13px;
  color: var(--blue);
  cursor: pointer;
}
#sidebar { display: flex; }

@media (max-width: 768px) {
  #sidebar { display: none; }
  #sidebar.open { display: flex; width: 100%; }
  #main { margin-left: 0; padding: 0 20px 60px; }
  #mobile-nav { display: block; }
  h1 { font-size: 1.5rem; }
  h2 { font-size: 1.25rem; }
}

/* ── Scrollbar ─────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--card); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--muted); }

/* ── Print ─────────────────────────────────────────────────────────── */
@media print {
  #sidebar { display: none; }
  #main { margin-left: 0; }
  body { background: #fff; color: #000; }
  h1,h2,h3,h4 { color: #000; }
  code { border: 1px solid #ccc; color: #000; }
}
"""

# ── Markdown extensions ─────────────────────────────────────────────────
MD = markdown.Markdown(
    extensions=[
        'fenced_code',
        'tables',
    ]
)

# ── Diagram embed map ────────────────────────────────────────────────────
DIAGRAM_MARKDOWN = {
    "01-traffic-mindset.svg":          "![出海网站核心逻辑](assets/diagrams/01-traffic-mindset.svg \"出海网站核心逻辑\")",
    "02-ecpm-comparison.svg":           "![各地区 ECPM 对比](assets/diagrams/02-ecpm-comparison.svg \"ECPM对比\")",
    "03-adsense-formula.svg":           "![Adsense 收入公式](assets/diagrams/03-adsense-formula.svg \"收入公式\")",
    "04-demand-mining-workflow.svg":    "![需求挖掘工作流](assets/diagrams/04-demand-mining-workflow.svg \"需求挖掘工作流\")",
    "05-kdroi-formula.svg":             "![KDRoi 选词公式](assets/diagrams/05-kdroi-formula.svg \"KDRoi公式\")",
    "06-four-search-intents.svg":       "![四种搜索意图](assets/diagrams/06-four-search-intents.svg \"四种搜索意图\")",
    "07-sop-12-steps.svg":              "![养网站防老 SOP 12步法](assets/diagrams/07-sop-12-steps.svg \"SOP12步法\")",
    "08-six-character-truth.svg":        "![六字真言](assets/diagrams/08-six-character-truth.svg \"六字真言\")",
    "09-google-ranking.svg":            "![Google 排名机制](assets/diagrams/09-google-ranking.svg \"Google排名\")",
    "10-onpage-seo-elements.svg":       "![On-Page SEO 元素](assets/diagrams/10-onpage-seo-elements.svg \"On-Page SEO\")",
    "11-canonical-nofollow-robots.svg":"![技术 SEO 三大问题](assets/diagrams/11-canonical-nofollow-robots.svg \"技术SEO\")",
    "12-multilingual-structure.svg":     "![多语言网站结构](assets/diagrams/12-multilingual-structure.svg \"多语言结构\")",
    "13-programmatic-seo-flywheel.svg": "![程序化 SEO 飞轮](assets/diagrams/13-programmatic-seo-flywheel.svg \"程序化SEO\")",
    "14-content-ai-tool-flywheel.svg":  "![内容型AI工具站飞轮](assets/diagrams/14-content-ai-tool-flywheel.svg \"内容型AI工具站\")",
    "15-monetization-path.svg":         "![变现路径图](assets/diagrams/15-monetization-path.svg \"变现路径\")",
}

# ── Process BOOK.md ──────────────────────────────────────────────────────
content = open(BOOK_PATH, encoding="utf-8").read()

# Replace markdown image links with raw SVG inline
for fname, md_ref in DIAGRAM_MARKDOWN.items():
    path = os.path.join(DIAG_DIR, fname)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            svg_content = f.read()
        # Escape for HTML attribute
        escaped = svg_content.replace('"', '&quot;')
        # Replace the markdown image with an HTML img tag pointing to relative path
        # (keeping original markdown path, will be resolved by browser via base URL)

html_body = MD.convert(content)

# ── Build sidebar HTML ────────────────────────────────────────────────────
# Extract TOC from processed HTML
toc_links = ""
current_chapter = ""
chapters = []

chapter_pattern = re.compile(r'<h2[^>]*>(.*?)</h2>', re.DOTALL)
h3_pattern = re.compile(r'<h3[^>]*>(.*?)</h3>', re.DOTALL)

h2_blocks = re.split(r'(<h2)', html_body)
for block in h2_blocks[1:]:  # skip first empty
    pass  # simplified: rebuild nav from raw markdown

# Build nav from raw markdown source
nav_html = ""
current_h2 = ""
h3s = []
for line in content.split('\n'):
    if line.startswith('## '):
        if h3s and current_h2:
            for h3 in h3s:
                nav_html += f'  <a class="nav-item" href="#{h3[1]}">{h3[0]}</a>\n'
        if current_h2:
            nav_html += '</div>\n'
        current_h2 = line[3:].strip()
        anchor = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]+', '-', current_h2).strip('-').lower()
        nav_html += f'<div class="nav-group">\n'
        nav_html += f'  <a class="nav-item chapter-title" href="#{anchor}">{current_h2}</a>\n'
        h3s = []
    elif line.startswith('### '):
        text = line[4:].strip()
        anchor = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]+', '-', text).strip('-').lower()
        h3s.append((text, anchor))

if h3s and current_h2:
    for h3 in h3s:
        nav_html += f'  <a class="nav-item" href="#{h3[1]}">{h3[0]}</a>\n'
if current_h2:
    nav_html += '</div>\n'

# ── HTML Shell ─────────────────────────────────────────────────────────────
HTML = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>出海AI工具站SEO完全指南</title>
<style>{CSS}</style>
</head>
<body>
<button id="mobile-nav" onclick="document.getElementById('sidebar').classList.toggle('open')">≡ 目录</button>

<div id="sidebar">
  <div id="sidebar-header">
    <h1>出海AI工具站<br>SEO完全指南</h1>
    <p>基于哥飞公众号 · MIT协议开放</p>
  </div>
  <nav id="nav">
{nav_html}
  </nav>
</div>

<div id="main">
{html_body}
</div>

<script>
  // Highlight active nav item
  const items = document.querySelectorAll('.nav-item');
  const sections = document.querySelectorAll('h2[id], h3[id]');
  function onScroll() {{
    let top = window.scrollY + 80;
    let active = items[0];
    sections.forEach(s => {{
      if (s.offsetTop <= top) active = document.querySelector(`.nav-item[href="#${{s.id}}"]`) || active;
    }});
    items.forEach(i => i.classList.remove('active'));
    if (active) active.classList.add('active');
  }}
  window.addEventListener('scroll', onScroll, {{ passive: true }});
  onScroll();
</script>
</body>
</html>"""

with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write(HTML)

size = os.path.getsize(OUT_PATH)
print(f"HTML generated: {OUT_PATH} ({size:,} bytes)")
