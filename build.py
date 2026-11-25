#!/usr/bin/env python3
"""Regenerate the static portfolio from reviewed bilingual JSON; standard library only."""
import html
import json
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
PROFILE = json.loads((ROOT / "content/profile.json").read_text())
PROJECTS = json.loads((ROOT / "content/projects.json").read_text())
MEDIA = json.loads((ROOT / "content/media.json").read_text())
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


def media_path(value):
    """Accept only existing, repository-local media, never external embeds."""
    if not isinstance(value, str):
        raise ValueError("Media src/poster must be a path string")
    parsed = urlsplit(value)
    path = Path(value)
    if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment or "\\" in value or path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Media must use a local assets/media path: {value!r}")
    if path.parts[:2] != ("assets", "media"):
        raise ValueError(f"Media must be inside assets/media: {value!r}")
    actual = (ROOT / path).resolve()
    if not actual.is_relative_to(ROOT.resolve()) or not actual.is_relative_to((ROOT / "assets/media").resolve()) or not actual.is_file():
        raise ValueError(f"Media file is missing or outside assets/media: {value!r}")
    return path.as_posix()


def check_media():
    if MEDIA.get("schema_version") != 1 or not isinstance(MEDIA.get("projects"), dict):
        raise ValueError("content/media.json needs schema_version 1 and a projects object")
    project_ids = {project["id"] for project in PROJECTS}
    for project_id, config in MEDIA["projects"].items():
        if project_id not in project_ids:
            raise ValueError(f"Unknown project id in media.json: {project_id}")
        if not isinstance(config, dict) or not isinstance(config.get("gallery", []), list):
            raise ValueError(f"Invalid media configuration for {project_id}")
        entries = ([config["thumbnail"]] if config.get("thumbnail") is not None else []) + config.get("gallery", [])
        for item in entries:
            if not isinstance(item, dict) or item.get("type") not in ("image", "video"):
                raise ValueError(f"Media in {project_id} must have type image or video")
            src = media_path(item.get("src"))
            extensions = {"image": {".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif"}, "video": {".mp4", ".webm"}}
            if Path(src).suffix.lower() not in extensions[item["type"]]:
                raise ValueError(f"Unsupported {item['type']} format: {src}")
            for field in ("alt", "caption"):
                if not isinstance(item.get(field), dict) or any(not isinstance(item[field].get(lang), str) for lang in ("zh", "en")):
                    raise ValueError(f"Media {field} needs zh and en text: {src}")
            if any(not item["alt"][lang].strip() for lang in ("zh", "en")):
                raise ValueError(f"Media alt text must not be empty: {src}")
            if item.get("poster"):
                poster = media_path(item["poster"])
                if item["type"] != "video" or Path(poster).suffix.lower() not in extensions["image"]:
                    raise ValueError(f"Only video may specify an image poster: {src}")


def media_element(item, lang, prefix=""):
    src = esc(prefix + item["src"])
    description = esc(tr(item["alt"], lang))
    if item["type"] == "image":
        return f'<img src="{src}" alt="{description}" loading="lazy" decoding="async">'
    poster = f' poster="{esc(prefix + item["poster"])}"' if item.get("poster") else ""
    return f'<video controls preload="metadata" playsinline aria-label="{description}"{poster}><source src="{src}" type="video/{"webm" if item["src"].lower().endswith(".webm") else "mp4"}"><p>{tx("浏览器不支持内嵌视频。","Your browser does not support embedded video.",lang)} <a href="{src}">{tx("打开视频文件","Open the video file",lang)}</a></p></video>'


def project_art(p, lang):
    item = MEDIA["projects"].get(p["id"], {}).get("thumbnail")
    if item is None:
        return f'<a class="project-art" href="{page_path(p,lang)}" aria-label="{esc(tr(p["title"],lang))}">{chart(p["chart"],lang)}</a>'
    visual = media_element(item, lang)
    caption = tr(item["caption"], lang)
    caption_html = f'<figcaption>{esc(caption)}</figcaption>' if caption.strip() else ""
    if item["type"] == "image":
        visual = f'<a href="{page_path(p,lang)}">{visual}</a>'
    return f'<figure class="project-art project-media">{visual}{caption_html}</figure>'


def project_gallery(p, lang):
    items = MEDIA["projects"].get(p["id"], {}).get("gallery", [])
    if not items:
        return ""
    figures = []
    for item in items:
        caption = tr(item["caption"], lang)
        caption_html = f'<figcaption>{esc(caption)}</figcaption>' if caption.strip() else ""
        figures.append(f'<figure class="media-figure">{media_element(item,lang,"../")}{caption_html}</figure>')
    return f'<section class="detail-section project-gallery"><h2>{tx("项目影像","Project media",lang)}</h2><div class="media-grid">{"".join(figures)}</div></section>'


def shell(title, description, body, lang, filename, *, detail=False, alternate=None):
    prefix = "/" if filename == "404.html" else "../" if detail else ""
    alternate = alternate or ("en.html" if lang == "zh" else "index.html")
    h = prefix + home(lang)
    nav = [
        ("about", "关于", "About"), ("news", "近况", "News"),
        ("education", "教育", "Education"), ("experience", "经历", "Experience"),
        ("projects", "项目", "Projects"), ("opensource", "开源", "Open source"),
        ("recognition", "成果", "Awards"), ("contact", "联系", "Contact"),
    ]
    nav_html = "".join(f'<a href="{h}#{key}">{tx(zh,en,lang)}</a>' for key, zh, en in nav)
    return f'''<!doctype html>
<html lang="{tx('zh-CN','en',lang)}">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(description)}">
<meta name="theme-color" content="#172b42"><meta name="color-scheme" content="light">
<link rel="canonical" href="{SITE}/{filename}"><link rel="icon" type="image/svg+xml" href="{prefix}assets/favicon.svg">
<meta property="og:type" content="website"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{SITE}/{filename}"><meta property="og:image" content="{SITE}/assets/portrait.png">
<link rel="stylesheet" href="{prefix}assets/style.css">
<script src="{prefix}assets/navigation.js" defer></script>
</head>
<body>
<a class="skip" href="#main">{tx('跳到正文','Skip to content',lang)}</a>
<header class="site-header"><div class="wrap header-inner"><a class="wordmark" href="{h}">{tx('张壮志','Zhuangzhi Zhang',lang)}<small>{tx('Zhuangzhi Zhang','张壮志',lang)}</small></a><button class="nav-toggle" type="button" aria-controls="site-nav" aria-expanded="false">{tx('目录','Menu',lang)} <span aria-hidden="true">☰</span></button><nav class="nav" id="site-nav" aria-label="{tx('主导航','Main navigation',lang)}">{nav_html}<a class="lang" href="{alternate}" lang="{tx('en','zh-CN',lang)}" hreflang="{tx('en','zh-CN',lang)}">{tx('EN','中文',lang)}</a></nav></div></header>
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
    rows = []
    for school in PROFILE["education"]:
        name = esc(tr(school["institution"], lang))
        url = esc(tr(school["website"], lang))
        dates = period(school, lang)
        if school["expected"]:
            dates += tx("（预计）", " (expected)", lang)
        rows.append(f'''<li class="school-row">
<a class="school-logo" href="{url}" aria-label="{name}" tabindex="-1"><img src="{esc(school['logo'])}" alt="" decoding="async"></a>
<div class="school-study"><h3><a href="{url}">{name}</a></h3>
<p>{esc(tr(school["degree"],lang))}</p><p>{esc(tr(school["note"],lang))}</p></div>
<div class="school-meta"><span>{esc(dates)}</span><span>{esc(tr(school["location"],lang))}</span></div></li>''')
    return '<ul class="school-list">' + ''.join(rows) + '</ul>'



def homepage(lang):
    university = PROFILE["education"][0]
    employer = PROFILE["experience"][0]
    intro = tx(
        "我做机器人学习与 AI 系统，主要研究视觉–语言–动作模型（VLA）的评测、推理优化和真机数据采集。我想弄清楚策略会在哪些场景下失败，以及怎样用这些失败指导下一轮训练。",
        "I work on robot learning and AI systems, focusing on vision–language–action (VLA) policy evaluation, inference optimization and real-robot data collection. I study where policies fail and how those failures can guide the next round of training.",
        lang,
    )
    featured_ids = ("vla-evaluation", "training-regression", "robot-data")
    by_id = {p["id"]: p for p in PROJECTS}
    rows = []
    for project_id in featured_ids:
        p = by_id[project_id]
        title = esc(tr(p["title"], lang))
        result = esc(tr(p["highlight"], lang))
        if project_id == "vla-evaluation":
            result = tx("在单张 RTX 4090D 上，500 次 LIBERO-Spatial 评测耗时从 55.8 分钟降到 32.0 分钟。", "On a single RTX 4090D, 500 LIBERO-Spatial episodes took 32.0 minutes, down from 55.8.", lang)
        rows.append(f'''<article class="project-row">{project_art(p,lang)}
<div class="project-copy"><h3><a href="{page_path(p,lang)}">{title}</a></h3>
<p class="project-highlight">{result}</p><p>{esc(tr(p["summary"],lang))}</p>
<a class="detail" href="{page_path(p,lang)}">{tx("实验详情","Experiment details",lang)}</a></div></article>''')
    other_projects = " · ".join(
        f'<a href="{page_path(p,lang)}">{esc(tr(p["title"],lang))}</a>'
        for p in PROJECTS if p["id"] not in featured_ids
    )
    research = {
        "start": PROFILE["education"][0]["start"], "end": "present",
        "organization": PROFILE["education"][0]["institution"],
        "role": {"zh": "硕士研究 · 柔性线缆仿真", "en": "Master’s research · Flexible cable simulation"},
        "description": [{"zh": "研究基于 PBD / XPBD 的柔性线缆仿真。", "en": "I study flexible cable simulation with position-based dynamics (PBD and XPBD)."}],
    }
    patents=[]
    for p in PROFILE['recognition']:
        if p['type']=='patent':
            patents.append(f'<article class="output-item"><h3>{esc(tr(p["title"],lang))}</h3><p>{esc(tr(p["category"],lang))} · {esc(tr(p["status"],lang))}<br>{esc(p["identifier"])} · {esc(tr(p["role"],lang))}</p></article>')
    awards=''.join(f'<li><small>{esc(a["date"] or "—")}</small><span>{esc(tr(a["title"],lang))}</span></li>' for a in PROFILE['recognition'] if a['type']=='award' and a['featured'])
    return f'''<main id="main" class="academic-home">
<section id="about" class="academic-hero" aria-labelledby="name">
<div class="hero-landscape" role="img" aria-label="{tx('雪山下的双臂机器人工作台，窗边有小猫，窗外有人骑摩托、登山。','A two-arm robot at a mountain workbench, with a sleeping cat, a motorcyclist and a climber.',lang)}"></div>
<div class="wrap hero-inner"><div class="hero-bio">
<h1 id="name">{esc(tr(PROFILE['name'],lang))} <span lang="{tx('en','zh-CN',lang)}">{tx('Zhuangzhi Zhang','张壮志',lang)}</span></h1>
<div class="hero-roles"><div><span>{tx('车辆工程硕士生','M.S. student · Vehicle Engineering',lang)}</span><a href="{esc(tr(university['website'],lang))}">{esc(tr(university['institution'],lang))}</a></div>
<div><span>{esc(tr(employer['role'],lang))}</span><a href="#experience">{esc(tr(employer['organization'],lang))}</a></div></div>
<p class="intro-copy">{esc(intro)}</p>
<div class="hero-actions"><a href="{cv(lang)}">{tx('简历','CV',lang)}</a><a href="{PROFILE['contact']['github']}">GitHub</a><a href="mailto:{PROFILE['contact']['email']}">{tx('邮箱','Email',lang)}</a></div></div>
<img class="hero-portrait" src="assets/portrait.png" width="319" height="382" alt="{esc(tr(PROFILE['name'],lang))}"></div></section>
<section id="news" class="profile-block tinted"><div class="wrap">
<h2>{tx('近况','News',lang)}</h2><div class="dated-row"><time datetime="2026-11">2026.11</time><p>{tx('整理并公开机器人评测、训推回归与数据采集项目记录。','Published project notes on robot evaluation, training regression checks and data collection.',lang)} <a href="{CATALOG}">{tx('项目目录','Project index',lang)}</a></p></div>
</div></section>
<section id="education" class="profile-block"><div class="wrap">
<h2>{tx('教育背景','Education',lang)}</h2>{education(lang)}</div></section>
<section id="experience" class="profile-block tinted"><div class="wrap">
<h2>{tx('研究与实习经历','Research & experience',lang)}</h2>{timeline([research, *PROFILE['experience']],lang)}</div></section>
<section id="projects" class="profile-block"><div class="wrap">
<h2>{tx('代表项目','Selected projects',lang)}</h2>{''.join(rows)}
<p class="related-projects">{tx('其他项目','More projects',lang)} · {other_projects}</p></div></section>
<section id="opensource" class="profile-block tinted"><div class="wrap">
<h2>{tx('公开项目与技术笔记','Public projects & technical notes',lang)}</h2>
<article class="resource-row"><div><h3><a href="{CATALOG}">Embodied AI Portfolio</a></h3><p>{tx('机器人学习项目目录，收录实验条件、性能对照和评测记录。','An index of robot learning projects, experiment settings, performance comparisons and evaluation records.',lang)}</p></div>
<a href="{CATALOG}" aria-label="{tx('打开 GitHub 项目目录','Open the project catalog on GitHub',lang)}">GitHub ↗</a></article>
</div></section>
<section class="profile-block" id="recognition"><div class="wrap"><h2>{tx('成果与荣誉','Selected outputs & awards',lang)}</h2>
<div class="outputs"><div>{''.join(patents)}<p class="copyright-note">{tx('另有 4 项软件著作权，涵盖林业无人机管理、运动仿真与采摘装备控制。','Four software copyright registrations cover forestry UAV management, motion simulation and harvesting equipment control.',lang)}</p></div><ul class="award-list">{awards}</ul></div></div></section>
<section id="contact" class="profile-block tinted"><div class="wrap contact-strip"><div>
<h2>{tx('联系','Contact',lang)}</h2><a href="mailto:{PROFILE['contact']['email']}">{esc(PROFILE['contact']['email'])}</a></div>
<a href="{cv(lang)}">{tx('完整简历与技术经历','Full CV & technical experience',lang)} →</a></div></section>
</main>'''


def projectpage(p, lang):
    results=''
    if p['results']:
        metrics=''.join(f'<div><div class="result-value">{esc(tr(r["value"],lang))}</div><div class="result-label">{esc(tr(r["label"],lang))}</div></div>' for r in p['results'])
        results=f'<section class="detail-section"><h2>{tx("观察到的结果","Observed results",lang)}</h2><div class="results">{metrics}</div></section>'
    work=''.join(f'<li>{esc(tr(item,lang))}</li>' for item in p['work'])
    return f'''<main id="main" class="wrap"><div class="detail-main"><div class="breadcrumb"><a href="../{home(lang)}#projects">{tx('精选项目','Selected projects',lang)}</a> / {esc(tr(p['category'],lang))}</div><header class="project-header"><div class="eyebrow">{p['period']} · {tx('原力灵机实习','Internship at Dexmal',lang)}</div><h1>{esc(tr(p['title'],lang))}</h1><p class="project-lead">{esc(tr(p['summary'],lang))}</p><div class="detail-meta">{' · '.join(esc(t) for t in p['tags'])}</div></header><figure class="detail-figure">{chart(p['chart'],lang)}<figcaption>{esc(tr(p['highlight'],lang))}</figcaption></figure>{project_gallery(p,lang)}<section class="detail-section"><h2>{tx('要解决的问题','The question',lang)}</h2><p>{esc(tr(p['question'],lang))}</p></section><section class="detail-section"><h2>{tx('我参与的工作','My contribution',lang)}</h2><ul>{work}</ul></section><section class="detail-section"><h2>{tx('条件与范围','Conditions and scope',lang)}</h2><p>{esc(tr(p['experiment'],lang))}</p></section>{results}<aside class="boundary"><h2>{tx('结果的适用范围','How to interpret the result',lang)}</h2><p>{esc(tr(p['boundary'],lang))}</p></aside><section class="detail-section"><h2>{tx('这项工作的启发','What I learned',lang)}</h2><p>{esc(tr(p['reflection'],lang))}</p></section><div class="project-nav"><a href="{CATALOG}">{tx('查看 GitHub 项目说明','Project notes on GitHub',lang)}</a><a href="../{home(lang)}#projects">{tx('返回全部项目','Back to all projects',lang)}</a></div></div></main>'''


def cvpage(lang):
    projects=''.join(f'<article class="cv-project"><h3>{esc(tr(p["title"],lang))}</h3><p>{esc(tr(p["summary"],lang))}</p><p>{esc(tr(p["highlight"],lang))}。 {esc(tr(p["boundary"],lang))}</p></article>' for p in PROJECTS)
    recognition=''.join(f'<li>{esc(tr(r["title"],lang))}{" · "+esc(tr(r["status"],lang)) if r.get("status") else ""}{" · "+esc(r["identifier"]) if r.get("identifier") else ""}{" · "+esc(r["date"]) if r.get("date") else ""}</li>' for r in PROFILE['recognition'])
    return f'''<main id="main" class="wrap cv-main"><header class="cv-top"><div><h1>{esc(tr(PROFILE['name'],lang))}</h1><p>{esc(tr(PROFILE['tagline'],lang))}</p><div class="contact-links"><a href="mailto:{PROFILE['contact']['email']}">{PROFILE['contact']['email']}</a><a href="{PROFILE['contact']['github']}">github.com/zsevene077-cyber</a></div></div><button class="print-button" type="button" onclick="window.print()">{tx('打印 / 保存 PDF','Print / Save PDF',lang)}</button></header><section><h2>{tx('教育背景','Education',lang)}</h2>{education(lang)}</section><section><h2>{tx('实习经历','Experience',lang)}</h2>{timeline(PROFILE['experience'],lang)}</section><section><h2>{tx('近期项目','Recent projects',lang)}</h2>{projects}</section><section><h2>{tx('技术与实践','Tools & practice',lang)}</h2><p>{' · '.join(esc(tr(s,lang)) for s in PROFILE['skills'])}</p></section><section><h2>{tx('成果与荣誉','Outputs & awards',lang)}</h2><ul>{recognition}</ul></section><p class="cv-fine">{tx('公开版简历 · 2026-11-20。项目数据为指定实验条件下的历史结果；完整条件见个人网站项目详情。','Public CV · 2026-11-20. Project measurements are historical results under specific experimental conditions; the project pages provide the full scope.',lang)} <a href="{SITE}">zsevene077-cyber.github.io</a></p></main>'''


def write(path, content):
    destination = ROOT / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content + "\n", encoding="utf-8")


check_media()
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
print('Generated 15 static HTML pages from profile, projects, and optional media JSON.')
