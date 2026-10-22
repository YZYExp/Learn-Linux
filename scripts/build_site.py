"""Build the Pages reading site from the book's single Markdown source tree."""
import argparse
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
from urllib.parse import unquote, urlsplit

import markdown
from build_book import load, validate

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/site'
PARTS = [
    ('01', '运行的基础', '硬件、启动、进程、内存与二进制接口。', 1, 5),
    ('02', '文件与持久化', '从一个文件名，走到缓存、磁盘与叠加视图。', 6, 9),
    ('03', '隔离与虚拟化', '看清容器、KVM、QEMU 各自放置的边界。', 10, 13),
    ('04', '生态与贯通', '连接网络、桌面、手机与跨系统的真实问题。', 14, 20),
]
DESCRIPTIONS = {
 '00':'从熟悉的工具出发，建立自底向上的阅读方法。',
 '01':'分清硬件、Linux 内核、用户态与发行版。',
 '02':'控制权如何从固件交给内核、init 与服务。',
 '03':'把资源共享、等待与 CPU 调度分别理解。',
 '04':'页表、缺页、写时复制与内存统计的不同口径。',
 '05':'同为 Linux，为什么二进制仍可能无法运行。',
 '06':'路径、dentry、inode 与打开状态怎样关联。',
 '07':'写成功、原子替换与持久保存不是同一保证。',
 '08':'一次文件请求怎样往返内核与用户态实现。',
 '09':'共享底层文件，保留各自的修改与删除视图。',
 '10':'资源视图、使用预算和访问权限分别由谁约束。',
 '11':'从镜像内容到一组被组织起来的 Linux 进程。',
 '12':'执行控制、地址转换与虚拟设备怎样协作。',
 '13':'指令翻译之外，还要满足哪些平台接口。',
 '14':'socket、网络命名空间、虚拟链路与转发。',
 '15':'受约束的内核扩展，与请求和完成的异步队列。',
 '16':'驱动、图形库、合成器与音频服务的职责。',
 '17':'把现象、指标、假设与验证分开记录。',
 '18':'同一内核之上，另一套运行时与应用平台。',
 '19':'相似的系统概念，不等于相同内核和接口。',
 '20':'在 Mac 上追踪一次 Linux 服务请求的跨层路径。',
}

class TextOnly(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]
    def handle_data(self,data):
        self.parts.append(data)

def plain(html):
    parser=TextOnly(); parser.feed(html)
    return re.sub(r'\s+',' ',' '.join(parser.parts)).strip()

class RewriteLinks(HTMLParser):
    def __init__(self, source, routes, base):
        super().__init__(convert_charrefs=False)
        self.source=source; self.routes=routes; self.base=base; self.output=[]
    def rewrite(self,value):
        if not value or value.startswith(('#','data:','mailto:','https:','http:')):
            return value
        u=urlsplit(value)
        source=(self.source.parent / unquote(u.path)).resolve()
        suffix=('#'+u.fragment) if u.fragment else ''
        if source in self.routes:
            return self.base+self.routes[source]+suffix
        if source.is_relative_to(ROOT/'assets'):
            return self.base+source.relative_to(ROOT).as_posix()+suffix
        if source.is_file() and source.is_relative_to(ROOT):
            return 'https://github.com/YZYExp/Learn-Linux/blob/main/'+source.relative_to(ROOT).as_posix()+suffix
        raise ValueError(f'Unresolved content link: {self.source.name}: {value}')
    def handle_starttag(self,tag,attrs):
        values=[]
        for key,value in attrs:
            if key in ('href','src'): value=self.rewrite(value)
            if value is None: values.append(key)
            else: values.append(f'{key}="{escape(value,quote=True)}"')
        if tag=='img':values.extend(['loading="lazy"','decoding="async"'])
        self.output.append('<'+tag+(' '+' '.join(values) if values else '')+'>')
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
    def handle_endtag(self,tag):self.output.append('</'+tag+'>')
    def handle_data(self,data):self.output.append(data)
    def handle_entityref(self,name):self.output.append('&'+name+';')
    def handle_charref(self,name):self.output.append('&#'+name+';')

def render(source,routes,base):
    converter=markdown.Markdown(extensions=['tables','fenced_code','toc','sane_lists'])
    html=converter.convert(source.read_text())
    rewrite=RewriteLinks(source,routes,base); rewrite.feed(html)
    return ''.join(rewrite.output), converter.toc

def page(title, description, body, base, book, reader=False):
    menu='<button class="icon-button mobile-only" data-menu-toggle aria-expanded="false" aria-controls="chapter-nav">目录</button>' if reader else ''
    return f'''<!doctype html>
<html lang="zh-CN" data-base="{escape(base)}"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)} · {escape(book['title'])}</title>
<meta name="description" content="{escape(description,quote=True)}"><meta name="theme-color" content="#f7f5ef">
<link rel="icon" href="{base}assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{base}assets/styles.css">
<script>try{{document.documentElement.dataset.theme=localStorage.getItem('linux-book-theme')||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light')}}catch(e){{}}</script>
<script src="{base}assets/app.js" defer></script></head>
<body class="{'reader' if reader else 'home'}">
<a class="skip-link" href="#main">跳到正文</a><div id="reading-progress" aria-hidden="true"></div>
<header class="site-header"><div class="shell"><a class="brand" href="{base}"><span class="brand-mark">L/</span><span class="brand-name">Linux，自底向上</span></a>
<nav class="top-nav" aria-label="主导航"><a href="{base}#chapters">全书目录</a><a href="{base}read/sources/">资料来源</a><a href="https://github.com/YZYExp/Learn-Linux">GitHub ↗</a></nav>
<div class="header-actions">{menu}<button class="icon-button" data-search-open aria-label="搜索全书">搜索 <kbd>⌘ K</kbd></button><button class="icon-button" data-theme-toggle aria-label="切换深浅主题">◐</button></div></div></header>
{body}
<footer class="site-footer shell"><span>Linux，自底向上 · 第 {escape(book['edition'])} 版</span><span><a href="{base}read/review/">交叉审稿记录</a> · <a href="https://github.com/YZYExp/Learn-Linux">编辑与反馈 ↗</a></span></footer>
<dialog id="search-dialog" class="search-dialog" aria-labelledby="search-title"><div class="dialog-header"><h2 id="search-title">搜索全书</h2><button class="icon-button" data-search-close aria-label="关闭搜索">关闭 ×</button></div><label class="sr-only" for="search-input">章节、概念或问题</label><input id="search-input" type="search" placeholder="试试 FUSE、写时复制、KVM…" autocomplete="off"><p class="search-hint">输入关键词，查找章节与正文。</p><div id="search-results" aria-live="polite"></div></dialog>
<dialog id="image-dialog" class="image-dialog" aria-label="查看原图"><button class="icon-button" data-image-close aria-label="关闭原图">关闭 ×</button><img alt=""><p></p></dialog>
</body></html>'''

def navigation(book,base,current):
    intro=book['chapters'][0]
    def link(ch):
        active=' class="active" aria-current="page"' if ch['slug']==current else ''
        label=ch['title'] if ch['id']=='00' else ch['id']+'　'+ch['title']
        return f'<li><a{active} href="{base}read/{ch["slug"]}/">{escape(label)}</a></li>'
    output=f'<aside id="chapter-nav" class="chapter-nav" aria-label="章节目录"><a class="nav-heading" href="{base}#chapters">全书目录</a><div class="nav-part"><ol>{link(intro)}</ol></div>'
    for number,title,_,first,last in PARTS:
        output+=f'<div class="nav-part"><strong>{number} / {title}</strong><ol>'
        output+=''.join(link(c) for c in book['chapters'] if first<=int(c['id'])<=last)
        output+='</ol></div>'
    output+='<div class="nav-part"><strong>附录与资料</strong><ol>'
    for c in book['appendices']:
        output+=f'<li><a href="{base}read/appendix-{Path(c["source"]).stem}/">{escape(c["title"])}</a></li>'
    output+=f'<li><a href="{base}read/sources/">来源总索引</a></li><li><a href="{base}read/review/">审稿与修订</a></li></ol></div></aside>'
    return output

def homepage(book,stats,base,epub_available=False):
    download_url=base+'downloads/Linux-From-the-Ground-Up.epub' if epub_available else 'https://github.com/YZYExp/Learn-Linux/actions/workflows/build-book.yml'
    download_label='下载 EPUB ↓' if epub_available else 'EPUB 构建与下载 ↗'
    download_attribute=' download' if epub_available else ''
    groups=''
    for number,title,description,first,last in PARTS:
        rows=''
        for c in book['chapters']:
            if not first<=int(c['id'])<=last:continue
            text=Path(ROOT/c['source']).read_text()
            minutes=max(1,round(len(re.findall(r'[\u4e00-\u9fff]',text))/400))
            rows+=f'<a class="chapter-row" href="{base}read/{c["slug"]}/"><span class="chapter-number">{c["id"]}</span><span class="chapter-summary"><h4>{escape(c["title"])}</h4><p>{DESCRIPTIONS[c["id"]]}</p></span><span class="chapter-meta">约 {minutes} 分钟 <span aria-hidden="true">↗</span></span></a>'
        groups+=f'<div class="part"><div class="part-heading"><span class="part-index">PART {number}</span><h3>{title}</h3><p>{description}</p></div><div class="chapter-list">{rows}</div></div>'
    gallery=''
    for slug,title,caption in [('08-fuse','FUSE','同一个文件接口，跨过内核与用户态。'),('09-overlayfs','OverlayFS','目录层怎样形成一份合并视图。'),('12-kvm','KVM','执行控制与设备后端的协作边界。')]:
        gallery+=f'<figure class="diagram-card"><a href="{base}read/{slug}/"><img src="{base}assets/images/{slug}.svg" alt="{title}机制图" loading="lazy"></a><figcaption><strong>{title}</strong><p>{caption}</p></figcaption></figure>'
    return f'''<main id="main" class="shell">
<section class="hero"><div class="hero-copy"><p class="eyebrow">一本有来源、能串起来的系统原理读本</p><h1 class="hero-title">Linux，<br>自底向上<span aria-hidden="true">。</span></h1><p class="hero-subtitle">沿着一个请求，看懂整个系统。</p><p class="hero-description">从硬件、进程和文件开始，走到容器、虚拟机与 Android。面向有技术背景的读者，解释机制如何工作，以及它们的边界在哪里。</p><div class="actions"><a class="button primary" href="{base}read/00-preface/">开始阅读 <span aria-hidden="true">→</span></a><a class="button secondary" href="{download_url}"{download_attribute}>{download_label}</a></div><div class="stats"><div class="stat"><strong>{stats['chapters']}</strong><span>正文章节</span></div><div class="stat"><strong>{stats['mechanism_diagrams']}</strong><span>机制图解</span></div><div class="stat"><strong>{stats['distinct_cited_urls']}</strong><span>资料来源</span></div></div></div><figure class="hero-art"><img src="{base}assets/images/cover.webp" alt="从芯片、内核到应用生态的分层城市，AI概念插画，非技术证据" fetchpriority="high"><figcaption>从硬件到生态 · 概念插画</figcaption></figure></section>
<section class="section"><div class="section-heading"><p class="eyebrow">先把边界放回原位</p><h2>从“会用”，走向“理解为什么”。</h2><p>按层次建立地图，再把熟悉的特性接回它们依赖的机制。</p></div><div class="learning-map"><div class="map-step"><span>01</span><strong>执行</strong><small>谁在运行，谁在等待</small></div><div class="map-step"><span>02</span><strong>数据</strong><small>名字、缓存与持久化</small></div><div class="map-step"><span>03</span><strong>边界</strong><small>视图、资源与虚拟机器</small></div><div class="map-step"><span>04</span><strong>生态</strong><small>接口如何长成平台</small></div></div></section>
<section id="chapters" class="section"><div class="section-heading"><p class="eyebrow">CONTENTS / 全书目录</p><h2>二十章，贯通一套系统。</h2><p>可以顺序读，也可以从熟悉的问题进入。预计阅读时长仅供安排节奏。</p></div>{groups}</section>
<section class="section"><div class="section-heading"><p class="eyebrow">把关系画出来</p><h2>看得见的机制，核查得到的解释。</h2><p>图解保留关键对象和边界；具体事实旁边，就有原始资料。</p></div><div class="gallery">{gallery}</div></section>
<section class="section callout"><p class="eyebrow">阅读方式由你决定</p><h2>在网页里读，或把整本书带走。</h2><p>网页版与 EPUB 来自同一份分章主稿。资料与交叉审稿记录随书公开。</p><div class="actions"><a class="button primary" href="{base}read/00-preface/">从导读开始 →</a><a class="button secondary" href="{base}read/sources/">查看资料来源</a><a class="button secondary" href="https://github.com/YZYExp/Learn-Linux/archive/refs/heads/main.zip">下载源文件 ↗</a></div></section></main>'''

def check_links(base):
    errors=[]; pages=list(OUT.rglob('*.html')); parsed={}
    class Collector(HTMLParser):
        def __init__(self):super().__init__();self.links=[];self.ids=set()
        def handle_starttag(self,tag,attrs):
            a=dict(attrs)
            if a.get('id'):self.ids.add(a['id'])
            for key in ('href','src'):
                if a.get(key):self.links.append(a[key])
    for file in pages:
        p=Collector();p.feed(file.read_text());parsed[file]=p
    for file,p in parsed.items():
        for link in p.links:
            u=urlsplit(link)
            if u.scheme or u.netloc:continue
            path=unquote(u.path)
            if not path:target=file
            elif path.startswith(base):target=OUT/path[len(base):]
            elif path.startswith('/'):
                errors.append(f'Wrong base path: {file}: {link}');continue
            else:target=(file.parent/path).resolve()
            if target.is_dir():target=target/'index.html'
            if not target.is_file():errors.append(f'Missing: {file.relative_to(OUT)}: {link}')
            elif u.fragment and target in parsed and unquote(u.fragment) not in parsed[target].ids:
                errors.append(f'Missing fragment: {file.relative_to(OUT)}: {link}')
    if errors:raise ValueError('\n'.join(errors))
    print(f'Checked {len(pages)} HTML pages: local resources and fragments pass.')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--base-path',default='/Learn-Linux/')
    parser.add_argument('--epub',type=Path,help='Optional validated EPUB to include as a direct download')
    args=parser.parse_args();base='/'+args.base_path.strip('/')+'/' if args.base_path.strip('/') else '/'
    book=load();stats,_=validate(book)
    epub=args.epub.resolve() if args.epub else None
    if epub is not None:
        from build_book import verify_epub
        verify_epub(epub,stats['mechanism_diagrams']+1)
    if OUT.exists():shutil.rmtree(OUT)
    OUT.mkdir(parents=True,exist_ok=True)
    shutil.copytree(ROOT/'assets',OUT/'assets',dirs_exist_ok=True)
    from PIL import Image
    with Image.open(ROOT/book['cover']) as im:
        im.convert('RGB').resize((800,1200)).save(OUT/'assets/images/cover.webp',quality=86)
    for name in ['styles.css','app.js','favicon.svg']:shutil.copyfile(ROOT/'site'/name,OUT/'assets'/name)
    docs=[dict(c) for c in book['chapters']]
    docs += [dict(c,slug='appendix-'+Path(c['source']).stem,id='附录') for c in book['appendices']]
    docs += [dict(title=title,source=source,slug=slug,id='资料') for title,source,slug in [
      ('来源总索引','references/index.md','sources'),
      ('交叉审稿与修订记录','references/reviews/summary.md','review'),
      ('运行基础专题审稿','references/reviews/execution-v2.md','review-execution'),
      ('文件与 I/O 专题审稿','references/reviews/io-v2.md','review-io'),
      ('虚拟化与平台专题审稿','references/reviews/vm-platform-v2.md','review-platform')]]
    routes={(ROOT/c['source']).resolve():'read/'+c['slug']+'/' for c in docs}
    search=[]
    for index,c in enumerate(docs):
        html,toc=render(ROOT/c['source'],routes,base);text=plain(html)
        previous=docs[index-1] if index>0 and index<23 else None
        following=docs[index+1] if index<22 else None
        pagination=''
        for label,node in [('上一章',previous),('下一章',following)]:
            if node:pagination+=f'<a href="{base}read/{node["slug"]}/"><small>{label}</small><strong>{escape(node["title"])}</strong></a>'
        body=f'<main id="main" class="reader-grid shell">'+navigation(book,base,c['slug'])+f'<div class="reading-pane"><div class="reading-meta"><nav class="breadcrumbs" aria-label="面包屑"><a href="{base}">首页</a><span> / </span><span>{escape(c["id"])}</span></nav><span>第 {book["edition"]} 版 · 资料核查 {book["date"]}</span></div><article class="prose">{html}</article><nav class="chapter-pagination" aria-label="章节翻页">{pagination}</nav></div><aside class="page-toc" aria-label="本页目录"><strong>本页目录</strong>{toc}</aside></main>'
        target=OUT/'read'/c['slug'];target.mkdir(parents=True,exist_ok=True)
        (target/'index.html').write_text(page(c['title'],text[:150],body,base,book,True))
        search.append({'title':c['title'],'url':base+routes[(ROOT/c['source']).resolve()],'text':text,'kind':c['id']})
    (OUT/'index.html').write_text(page('在线阅读',book['description'],homepage(book,stats,base,epub is not None),base,book))
    (OUT/'search-index.json').write_text(json.dumps(search,ensure_ascii=False))
    if epub is not None:
        downloads=OUT/'downloads';downloads.mkdir(exist_ok=True)
        shutil.copyfile(epub,downloads/'Linux-From-the-Ground-Up.epub')
    (OUT/'.nojekyll').write_text('')
    check_links(base)
    print(f'Built website from {len(docs)} source documents at {OUT}; base {base}')

if __name__=='__main__':main()
