"""Validate the source tree, then build one Markdown and an illustrated EPUB."""
import argparse
import json
import io
from pathlib import Path
import posixpath
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'build'

def load():
    return json.loads((ROOT / 'book.json').read_text())

def source_files(book):
    return [ROOT / x['source'] for x in book['chapters'] + book.get('cases',[]) + book['appendices']]

def verify_png(source):
    from PIL import Image
    # Check PNG structure/CRC and fully decode its pixels.
    with Image.open(source) as image:
        image.verify()
    if hasattr(source, 'seek'):
        source.seek(0)
    with Image.open(source) as image:
        image.load()

def verify_epub(path, expected_images):
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        if archive.read('mimetype') != b'application/epub+zip':
            raise ValueError('Invalid EPUB mimetype')
        images = [n for n in names if n.endswith('.png')]
        if len(images) != expected_images:
            raise ValueError(f'Expected {expected_images} embedded images, found {len(images)}')
        for name in images:
            verify_png(io.BytesIO(archive.read(name)))
        for name in names:
            if name.endswith(('.xhtml', '.xml', '.opf', '.ncx')):
                root = ET.fromstring(archive.read(name))
                for element in root.iter():
                    src = element.attrib.get('src')
                    if src and not src.startswith(('data:', 'http:', 'https:')):
                        target = posixpath.normpath(posixpath.join(posixpath.dirname(name),src.split('#')[0]))
                        if target not in names:
                            raise ValueError(f'Missing EPUB resource: {name}: {src}')
    return {'embedded_png_images':len(images), 'epub_image_decode':'pass', 'epub_xml_and_image_paths':'pass'}

def validate(book):
    errors = []
    ids, slugs, order = set(), set(), []
    links, han = set(), 0
    expected_headers = {
        x['source']: ('# '+x['title'] if x['id']=='00'
                     else '# 第 '+str(int(x['id']))+' 章　'+x['title'])
        for x in book['chapters']
    }
    expected_headers.update({x['source']:'# '+x['title'] for x in book.get('cases',[])})
    for chapter in book['chapters']:
        if chapter['id'] in ids or chapter['slug'] in slugs:
            errors.append('duplicate chapter id or slug')
        ids.add(chapter['id']); slugs.add(chapter['slug']); order.append(chapter['order'])
    if order != list(range(len(order))):
        errors.append('chapter order is not continuous')
    for path in source_files(book):
        if not path.is_file():
            errors.append(f'missing: {path.relative_to(ROOT)}'); continue
        text = path.read_text()
        source = path.relative_to(ROOT).as_posix()
        if source in expected_headers and text.splitlines()[0] != expected_headers[source]:
            errors.append(f'chapter title differs from manifest: {path.name}')
        han += len(re.findall(r'[\u4e00-\u9fff]', text))
        if len(re.findall(r'^```', text, re.M)) % 2:
            errors.append(f'unbalanced fences: {path.name}')
        if re.search(r'\bTODO\b|待补正文|待生成配图|图片占位', text):
            errors.append(f'placeholder: {path.name}')
        for target in re.findall(r'\]\(([^)]+)\)', text):
            if target.startswith(('https://','http://')):
                links.add(target)
            elif not target.startswith('#'):
                if not (path.parent / target.split('#')[0]).resolve().exists():
                    errors.append(f'broken local link: {path.name}: {target}')
        if path.parent.name in ('chapters','cases') and not path.name.startswith('00-'):
            if '![' not in text or 'https://' not in text:
                errors.append(f'missing illustration or source: {path.name}')
    for path in (ROOT/'assets/images').glob('*.svg'):
        ET.parse(path)
    records = []
    for path in (ROOT/'references').glob('*-sources.json'):
        data = json.loads(path.read_text())
        records.extend(data if isinstance(data,list) else data.get('sources',[]))
    registered = {r['url'].split('#')[0] for r in records}
    missing = sorted(u for u in links if u.split('#')[0] not in registered)
    if missing:
        errors += ['unregistered citation: '+u for u in missing]
    root_commit = subprocess.check_output(['git','rev-list','--max-parents=0','HEAD'],cwd=ROOT,text=True).strip()
    first_tree = subprocess.check_output(['git','ls-tree','-r','--name-only',root_commit],cwd=ROOT,text=True).splitlines()
    first_readme = subprocess.check_output(['git','show',root_commit+':README.md'],cwd=ROOT)
    if first_tree != ['README.md'] or first_readme != b'':
        errors.append('root commit must contain only empty README.md')
    if errors:
        raise SystemExit('\n'.join(errors))
    result = {'chapters':len(book['chapters'])-1,'preface':1,'cases':len(book.get('cases',[])),'appendices':len(book['appendices']),
      'han_characters':han,'mechanism_diagrams':len(list((ROOT/'assets/images').glob('*.svg'))),
      'distinct_cited_urls':len({u.split('#')[0] for u in links}),'registered_sources':len(registered),
      'local_links':'pass','fences':'pass','chapter_titles':'pass',
      'root_commit':root_commit,'root_commit_empty_readme':'pass'}
    return result, records

def write_source_index(records):
    merged = {}
    for record in records:
        merged.setdefault(record['url'],record)
    sources = '# 来源总索引\n\n各段证据见正文就近链接；这里按 URL 去重，支持范围详见 JSON 登记。\n\n'
    for n,record in enumerate(sorted(merged.values(),key=lambda r:r['url']),1):
        sources += f"{n}. [{record['title']}]({record['url']})\n"
    (ROOT/'references/index.md').write_text(sources)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check-only',action='store_true')
    args = parser.parse_args()
    book = load(); result, records = validate(book)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if args.check_only:
        return
    BUILD.mkdir(exist_ok=True)
    toc = '\n'.join('- '+x['title'] for x in book['chapters']+book.get('cases',[])+book['appendices'])
    content = f"# {book['title']}\n\n{book['subtitle']}\n\n版本 {book['edition']} · {book['date']}\n\n![封面概念插画，AI 生成，非机制图](../{book['cover']})\n\n# 总目录\n\n{toc}\n\n"
    for path in source_files(book):
        content += path.read_text().strip()+'\n\n'
    (BUILD/'Linux-From-the-Ground-Up.md').write_text(content)
    write_source_index(records)
    (BUILD/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    pandoc = shutil.which('pandoc'); inkscape = shutil.which('inkscape')
    if not pandoc or not inkscape:
        raise SystemExit('EPUB requires pandoc and inkscape. Markdown was built successfully.')
    image_dir = BUILD/'epub-images'; image_dir.mkdir(exist_ok=True)
    for svg in sorted((ROOT/'assets/images').glob('*.svg')):
        output = image_dir/(svg.stem+'.png')
        temporary = image_dir/(svg.stem+'.export.png')
        subprocess.run([inkscape,str(svg),'--batch-process','--export-type=png','--export-filename='+str(temporary),'--export-width=1800'],
          check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        verify_png(temporary)
        temporary.replace(output)
    # Cover is carried by EPUB metadata, avoiding a duplicate picture in the text.
    epub_content = re.sub(r'!\[封面概念插画[^\]]*\]\([^\n]+\)\n','',content)
    epub_content = re.sub(r'\.\./assets/images/([^ )]+)\.svg',r'epub-images/\1.png',epub_content)
    (BUILD/'epub-source.md').write_text(epub_content)
    subprocess.run([pandoc,'epub-source.md','--from=markdown','--to=epub3','--toc',
      '--metadata=title:'+book['title'],'--metadata=subtitle:'+book['subtitle'],
      '--metadata=lang:zh-CN','--metadata=date:'+book['date'],
      '--epub-cover-image='+str(ROOT/book['cover']), '--css='+str(ROOT/'scripts/epub.css'),
      '--output=Linux-From-the-Ground-Up.epub'],cwd=BUILD,check=True)
    result.update(verify_epub(BUILD/'Linux-From-the-Ground-Up.epub',
                  len(list((ROOT/'assets/images').glob('*.svg')))+1))
    (BUILD/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('Built Markdown, source index, PNG illustrations and EPUB.')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__ == '__main__':
    main()
