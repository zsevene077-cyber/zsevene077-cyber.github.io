#!/usr/bin/env python3
"""Regenerate the static portfolio from reviewed bilingual JSON; standard library only."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROFILE = json.loads((ROOT / "content/profile.json").read_text())
PROJECTS = json.loads((ROOT / "content/projects.json").read_text())
SITE = "https://zsevene077-cyber.github.io"
CATALOG = "https://github.com/zsevene077-cyber/embodied-ai-portfolio"


def esc(value):
    return html.escape(str(value), quote=True)


def tr(value, lang):
    return value[lang] if isinstance(value, dict) else value


def tx(zh, en, lang):
    return zh if lang == "zh" else en


def period(item, lang):
    end = tx("至今", "Present", lang) if item["end"] == "present" else item["end"].replace("-", ".")
    return item["start"].replace("-", ".") + " – " + end


def page_path(project, lang):
    return f'projects/{project["id"]}{"-en" if lang == "en" else ""}.html'


def home(lang):
    return "en.html" if lang == "en" else "index.html"


def cv(lang):
    return "cv-en.html" if lang == "en" else "cv.html"


def shell(title, description, body, lang, filename, *, detail=False, alternate=None):
    prefix = "/" if filename == "404.html" else "../" if detail else ""
    alternate = alternate or ("en.html" if lang == "zh" else "index.html")
    h = prefix + home(lang)
    nav = [("about", "关于", "About", "optional"), ("projects", "项目", "Projects", ""), ("experience", "经历", "Experience", "optional"), ("contact", "联系", "Contact", "")]
    nav_html = "".join(f'<a class="{c}" href="{h}#{key}">{tx(zh,en,lang)}</a>' for key, zh, en, c in nav)
    return f'''<!doctype html>
<html lang="{tx('zh-CN','en',lang)}">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(description)}">
<meta name="theme-color" content="#172b42"><meta name="color-scheme" content="light">
<link rel="canonical" href="{SITE}/{filename}"><link rel="icon" type="image/svg+xml" href="{prefix}assets/favicon.svg">
<meta property="og:type" content="website"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{SITE}/{filename}"><meta property="og:image" content="{SITE}/assets/portrait.png">
<link rel="stylesheet" href="{prefix}assets/style.css">
</head>
<body>
<a class="skip" href="#main">{tx('跳到正文','Skip to content',lang)}</a>
<header class="site-header"><div class="wrap header-inner"><a class="wordmark" href="{h}">{tx('张壮志','Zhuangzhi Zhang',lang)}<small>{tx('Zhuangzhi Zhang','张壮志',lang)}</small></a><nav class="nav" aria-label="{tx('主导航','Main navigation',lang)}">{nav_html}<a class="lang" href="{alternate}" lang="{tx('en','zh-CN',lang)}" hreflang="{tx('en','zh-CN',lang)}">{tx('EN','中文',lang)}</a></nav></div></header>
{body}
<footer class="site-footer"><div class="wrap footer-inner"><span>© 2026 {esc(tr(PROFILE['name'],lang))}</span><span>{tx('更新于 2026 年 11 月','Updated November 2026',lang)} · <a href="{PROFILE['contact']['github']}/zsevene077-cyber.github.io">{tx('网站源码','Website source',lang)}</a></span></div></footer>
</body></html>'''


def chart(kind, lang):
    title = {
        "libero": tx("500 episodes 评测耗时：55.8 分钟与 32.0 分钟", "500-episode evaluation time: 55.8 and 32.0 minutes", lang),
        "transcode": tx("转码耗时：4 路 63.517 秒，8 路 41.265 秒", "Transcoding time: 63.517 seconds at 4 streams and 41.265 at 8", lang),
        "protocol": tx("32 个入口：27 个严格通过、4 个保留异常、1 个待完成", "32 entries: 27 strict passes, 4 with anomalies, 1 pending", lang),
        "lifecycle": tx("实验生命周期：配置、提交、监控、审计、归档、回收", "Experiment lifecycle: configure, submit, monitor, audit, archive, release", lang),
        "coverage": tx("四套 LIBERO，每套 500 episodes，完整覆盖 2000 个唯一 episode", "Four LIBERO suites with 500 episodes each; 2,000 unique episodes covered", lang)
    }[kind]
    start = f'<svg viewBox="0 0 320 190" role="img" aria-label="{esc(title)}" xmlns="http://www.w3.org/2000/svg"><title>{esc(title)}</title><g font-family="-apple-system,BlinkMacSystemFont,Segoe UI,PingFang SC,sans-serif" fill="#172b42">'
    if kind in ("libero", "transcode"):
        labels = ["2 workers", "10 workers"] if kind == "libero" else [tx("4 路并行","4 streams",lang),tx("8 路并行","8 streams",lang)]
        values = ["55.8 min", "32.0 min"] if kind == "libero" else ["63.517 s", "41.265 s"]
        ratio = 32/55.8 if kind == "libero" else 41.265/63.517
        content = f'<text x="8" y="24" font-size="15" fill="#586777">{tx("评测耗时" if kind=="libero" else "转码耗时","Elapsed time",lang)}</text><text x="8" y="56" font-size="16">{labels[0]}</text><text x="309" y="56" text-anchor="end" font-size="19" font-weight="600">{values[0]}</text><rect x="8" y="68" width="302" height="20" rx="2" fill="#bccbd7"/><text x="8" y="119" font-size="16">{labels[1]}</text><text x="309" y="119" text-anchor="end" font-size="19" font-weight="600" fill="#225d92">{values[1]}</text><rect x="8" y="131" width="{302*ratio:.1f}" height="20" rx="2" fill="#225d92"/><text x="8" y="181" font-size="14" fill="#586777">{tx("固定 500 episodes · 单 seed" if kind=="libero" else "同两条录制 · 3,090 帧","Fixed 500 episodes · one seed" if kind=="libero" else "Same recordings · 3,090 frames",lang)}</text>'
    elif kind == "protocol":
        blocks = ''.join(f'<rect x="{10+(i%8)*38}" y="{10+(i//8)*26}" width="29" height="18" rx="2" fill="{ "#225d92" if i<27 else "#c89545" if i<31 else "#d9e1e7"}"/>' for i in range(32))
        content = blocks + f'<text x="9" y="145" font-size="25" font-weight="600" fill="#225d92">27</text><text x="53" y="145" font-size="16">{tx("严格通过","strict passes",lang)}</text><text x="9" y="177" font-size="14" fill="#586777">{tx("4 个保留异常 / 1 个待完成","4 with anomalies / 1 pending",lang)}</text>'
    elif kind == "lifecycle":
        labels = [tx("配置","Configure",lang),tx("提交","Submit",lang),tx("监控","Monitor",lang),tx("审计","Audit",lang),tx("归档","Archive",lang),tx("回收","Release",lang)]
        content = '<path d="M55 58H265V137H55" fill="none" stroke="#b9cbd8" stroke-width="2"/>'
        positions = [(9,29),(117,29),(225,29),(225,108),(117,108),(9,108)]
        for label,(x,y) in zip(labels,positions):
            content += f'<rect x="{x}" y="{y}" width="85" height="54" rx="3" fill="#fff" stroke="#b9cbd8"/><text x="{x+42.5}" y="{y+33}" text-anchor="middle" font-size="15" fill="#225d92">{label}</text>'
    else:
        content = ''
        for i,(label,rate) in enumerate([("Spatial","490 / 500"),("Object","497 / 500"),("Goal","485 / 500"),("LIBERO-10","461 / 500")]):
            y=29+i*42
            content += f'<text x="8" y="{y}" font-size="15">{label}</text><text x="310" y="{y}" text-anchor="end" font-size="16" fill="#225d92">{rate}</text><line x1="8" y1="{y+12}" x2="310" y2="{y+12}" stroke="#c9d7e2" stroke-width="5"/><line x1="8" y1="{y+12}" x2="{8+302*int(rate.split()[0])/500:.1f}" y2="{y+12}" stroke="#225d92" stroke-width="5"/>'
    return start+content+'</g></svg>'


def timeline(items, lang):
    content = []
    for item in items:
        descriptions = ''.join(f'<p>{esc(tr(p,lang))}</p>' for p in item['description'])
        content.append(f'<article class="timeline-item"><div class="timeline-date">{period(item,lang)}</div><div class="timeline-body"><h3>{esc(tr(item["organization"],lang))}</h3><div class="timeline-role">{esc(tr(item["role"],lang))}</div>{descriptions}</div></article>')
    return '<div class="experience-list">'+''.join(content)+'</div>'


def education(lang):
    return ''.join(f'<article class="education-item"><h3>{esc(tr(e["institution"],lang))}</h3><p>{esc(tr(e["degree"],lang))}</p><div class="date">{period(e,lang)}{tx("（预计）"," (expected)",lang) if e["expected"] else ""}</div><p>{esc(tr(e["note"],lang))}</p></article>' for e in PROFILE['education'])


def homepage(lang):
    bio = ''.join(f'<p>{esc(tr(b,lang))}</p>' for b in PROFILE['bio'][:2])
    rows=[]
    for p in PROJECTS:
        tags = ''.join(f'<span class="tag">{esc(t)}</span>' for t in p['tags'][:3])
        rows.append(f'<article class="project-row"><a class="project-art" href="{page_path(p,lang)}" aria-label="{esc(tr(p["title"],lang))}">{chart(p["chart"],lang)}</a><div class="project-copy"><div class="eyebrow">{esc(tr(p["category"],lang))}</div><h3><a href="{page_path(p,lang)}">{esc(tr(p["title"],lang))}</a></h3><p>{esc(tr(p["summary"],lang))}</p><p class="project-highlight">{esc(tr(p["highlight"],lang))}</p><div class="project-meta">{tags}<a class="detail" href="{page_path(p,lang)}">{tx("项目详情","Read the project",lang)}</a></div></div></article>')
    patents=[]
    for p in PROFILE['recognition']:
        if p['type']=='patent':
            patents.append(f'<article class="output-item"><h3>{esc(tr(p["title"],lang))}</h3><p>{esc(tr(p["category"],lang))} · {esc(tr(p["status"],lang))}<br>{esc(p["identifier"])} · {esc(tr(p["role"],lang))}</p></article>')
    awards=''.join(f'<li><small>{esc(a["date"] or "—")}</small><span>{esc(tr(a["title"],lang))}</span></li>' for a in PROFILE['recognition'] if a['type']=='award' and a['featured'])
    skills=''.join(f'<span>{esc(tr(s,lang))}</span>' for s in PROFILE['skills'])
    return f'''<main id="main" class="wrap">
<section id="about" class="hero" aria-labelledby="name"><div class="hero-text"><div class="eyebrow">ROBOT LEARNING & AI SYSTEMS</div><h1 id="name">{esc(tr(PROFILE['name'],lang))}<span class="name-en">{tx('Zhuangzhi Zhang','张壮志',lang)}</span></h1><p class="hero-role">{tx('北京理工大学硕士研究生 · 原力灵机 AI Infra 实习生','M.S. student at BIT · AI Infrastructure Intern at Dexmal',lang)}</p><div class="bio">{bio}</div><div class="contact-links"><a href="mailto:{PROFILE['contact']['email']}">{tx('邮箱','Email',lang)}</a><a href="{PROFILE['contact']['github']}">GitHub</a><a href="{cv(lang)}">{tx('简历','CV',lang)}</a></div></div><figure class="portrait"><img src="assets/portrait.png" alt="{tx('张壮志的个人照片','Portrait of Zhuangzhi Zhang',lang)}" width="319" height="382"><figcaption>{tx('北京，中国','Beijing, China',lang)}<br>{tx('机器人学习与 AI 系统','Robot learning & AI systems',lang)}</figcaption></figure></section>
<div class="focus-line"><strong>{tx('当前关注','Current interests',lang)}</strong><span>{tx('VLA 评测　/　模型部署　/　机器人数据','VLA evaluation　/　Model serving　/　Robot data',lang)}</span></div>
<section id="projects" class="section"><div class="section-heading"><div><h2>{tx('精选项目','Selected projects',lang)}</h2><p>{tx('从实验配置到数据与结果，记录我参与的工程实践。','Engineering work connecting experiment setup, data, and results.',lang)}</p></div><a href="{CATALOG}">{tx('GitHub 项目目录','Project catalog on GitHub',lang)}</a></div>{''.join(rows)}</section>
<section id="experience" class="section"><div class="section-heading"><h2>{tx('实习经历','Experience',lang)}</h2></div>{timeline(PROFILE['experience'],lang)}</section>
<section class="section two-columns" id="education"><div><h2 class="subheading">{tx('教育背景','Education',lang)}</h2>{education(lang)}</div><div><h2 class="subheading">{tx('技术与实践','Tools & practice',lang)}</h2><div class="skill-list">{skills}</div><p style="font-size:16px;color:var(--muted);margin-top:23px">{esc(tr(PROFILE['bio'][2],lang))}</p></div></section>
<section class="section" id="recognition"><div class="section-heading"><h2>{tx('成果与荣誉','Selected outputs & awards',lang)}</h2><a href="{cv(lang)}">{tx('完整简历','Full CV',lang)}</a></div><div class="outputs"><div>{''.join(patents)}<p style="font-size:15px;color:var(--muted);margin-top:13px">{tx('另有 4 项软件著作权，涵盖林业无人机管理、运动仿真与采摘装备控制。','Four software copyright registrations cover forestry UAV management, motion simulation, and harvesting-device control.',lang)}</p></div><ul class="award-list">{awards}</ul></div></section>
<section id="contact" class="contact-section"><div><h2>{tx('保持联系','Get in touch',lang)}</h2><p>{tx('欢迎交流机器人学习、评测与 AI Infra 相关问题。','I welcome conversations about robot learning, evaluation, and AI infrastructure.',lang)}</p></div><a class="email-link" href="mailto:{PROFILE['contact']['email']}">{PROFILE['contact']['email']}</a></section>
</main>'''


def projectpage(p, lang):
    results=''
    if p['results']:
        metrics=''.join(f'<div><div class="result-value">{esc(tr(r["value"],lang))}</div><div class="result-label">{esc(tr(r["label"],lang))}</div></div>' for r in p['results'])
        results=f'<section class="detail-section"><h2>{tx("观察到的结果","Observed results",lang)}</h2><div class="results">{metrics}</div></section>'
    work=''.join(f'<li>{esc(tr(item,lang))}</li>' for item in p['work'])
    return f'''<main id="main" class="wrap"><div class="detail-main"><div class="breadcrumb"><a href="../{home(lang)}#projects">{tx('精选项目','Selected projects',lang)}</a> / {esc(tr(p['category'],lang))}</div><header class="project-header"><div class="eyebrow">{p['period']} · {tx('原力灵机实习','Internship at Dexmal',lang)}</div><h1>{esc(tr(p['title'],lang))}</h1><p class="project-lead">{esc(tr(p['summary'],lang))}</p><div class="detail-meta">{' · '.join(esc(t) for t in p['tags'])}</div></header><figure class="detail-figure">{chart(p['chart'],lang)}<figcaption>{esc(tr(p['highlight'],lang))}</figcaption></figure><section class="detail-section"><h2>{tx('要解决的问题','The question',lang)}</h2><p>{esc(tr(p['question'],lang))}</p></section><section class="detail-section"><h2>{tx('我参与的工作','My contribution',lang)}</h2><ul>{work}</ul></section><section class="detail-section"><h2>{tx('条件与范围','Conditions and scope',lang)}</h2><p>{esc(tr(p['experiment'],lang))}</p></section>{results}<aside class="boundary"><h2>{tx('结果的适用范围','How to interpret the result',lang)}</h2><p>{esc(tr(p['boundary'],lang))}</p></aside><section class="detail-section"><h2>{tx('这项工作的启发','What I learned',lang)}</h2><p>{esc(tr(p['reflection'],lang))}</p></section><div class="project-nav"><a href="{CATALOG}">{tx('查看 GitHub 项目说明','Project notes on GitHub',lang)}</a><a href="../{home(lang)}#projects">{tx('返回全部项目','Back to all projects',lang)}</a></div></div></main>'''


def cvpage(lang):
    projects=''.join(f'<article class="cv-project"><h3>{esc(tr(p["title"],lang))}</h3><p>{esc(tr(p["summary"],lang))}</p><p>{esc(tr(p["highlight"],lang))}。 {esc(tr(p["boundary"],lang))}</p></article>' for p in PROJECTS)
    recognition=''.join(f'<li>{esc(tr(r["title"],lang))}{" · "+esc(tr(r["status"],lang)) if r.get("status") else ""}{" · "+esc(r["identifier"]) if r.get("identifier") else ""}{" · "+esc(r["date"]) if r.get("date") else ""}</li>' for r in PROFILE['recognition'])
    return f'''<main id="main" class="wrap cv-main"><header class="cv-top"><div><h1>{esc(tr(PROFILE['name'],lang))}</h1><p>{esc(tr(PROFILE['tagline'],lang))}</p><div class="contact-links"><a href="mailto:{PROFILE['contact']['email']}">{PROFILE['contact']['email']}</a><a href="{PROFILE['contact']['github']}">github.com/zsevene077-cyber</a></div></div><button class="print-button" type="button" onclick="window.print()">{tx('打印 / 保存 PDF','Print / Save PDF',lang)}</button></header><section><h2>{tx('教育背景','Education',lang)}</h2>{education(lang)}</section><section><h2>{tx('实习经历','Experience',lang)}</h2>{timeline(PROFILE['experience'],lang)}</section><section><h2>{tx('近期项目','Recent projects',lang)}</h2>{projects}</section><section><h2>{tx('技术与实践','Tools & practice',lang)}</h2><p>{' · '.join(esc(tr(s,lang)) for s in PROFILE['skills'])}</p></section><section><h2>{tx('成果与荣誉','Outputs & awards',lang)}</h2><ul>{recognition}</ul></section><p class="cv-fine">{tx('公开版简历 · 2026-11-20。项目数据为指定实验条件下的历史结果；完整条件见个人网站项目详情。','Public CV · 2026-11-20. Project measurements are historical results under specific experimental conditions; the project pages provide the full scope.',lang)} <a href="{SITE}">zsevene077-cyber.github.io</a></p></main>'''


def write(path, content):
    destination = ROOT / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content + "\n", encoding="utf-8")


for language in ('zh','en'):
    site_title = tx('张壮志 · 机器人学习与 AI 系统','Zhuangzhi Zhang · Robot Learning & AI Systems',language)
    description = tr(PROFILE['bio'][0],language)
    write(home(language), shell(site_title, description, homepage(language), language, home(language)))
    write(cv(language), shell(tx('张壮志 · 简历','Zhuangzhi Zhang · CV',language),description,cvpage(language),language,cv(language),alternate=cv('en' if language=='zh' else 'zh')))
    for project in PROJECTS:
        filename = page_path(project,language)
        alternate = page_path(project,'en' if language=='zh' else 'zh').split('/')[-1]
        write(filename,shell(tr(project['title'],language)+' · '+tr(PROFILE['name'],language),tr(project['summary'],language),projectpage(project,language),language,filename,detail=True,alternate=alternate))
write('404.html',shell('页面未找到 · 张壮志','页面未找到。','<main id="main" class="wrap not-found"><h1>页面未找到</h1><p>这个链接可能已更新。可以从首页继续浏览项目与经历。</p><a href="/">返回首页</a></main>','zh','404.html'))
print('Generated 15 static HTML pages from content/profile.json and content/projects.json.')
