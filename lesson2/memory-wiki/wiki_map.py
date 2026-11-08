"""Generate an offline HTML map from the Markdown pages in a published wiki."""

import argparse
import json
from pathlib import Path
import posixpath
import re
from urllib.parse import unquote


LINK = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^)\s]+)\)")


def render_wiki(directory):
    root = directory.resolve()
    pages = {}
    for path in sorted(root.rglob("*.md")):
        relative = path.relative_to(root)
        if not path.is_file() or not path.resolve().is_relative_to(root) or any(part.startswith(".") for part in relative.parts):
            continue
        body = path.read_text(encoding="utf-8")
        heading = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
        pages[relative.as_posix()] = {"title": heading[1] if heading else path.stem, "body": body, "links": {}}
    if "index.md" not in pages:
        raise ValueError("The published wiki needs an index.md.")

    edges = set()
    for path, page in pages.items():
        for href in LINK.findall(page["body"]):
            target = unquote(re.split(r"[#?]", href, maxsplit=1)[0])
            if not target or target.startswith("/") or ":" in target:
                continue
            linked = posixpath.normpath(posixpath.join(posixpath.dirname(path), target))
            if linked in pages and linked != path:
                page["links"][href] = linked
                edges.add(tuple(sorted((path, linked))))

    payload = json.dumps({"pages": pages, "edges": sorted(edges)}, ensure_ascii=False).replace("<", "\\u003c")
    return HTML.replace("/* WIKI_DATA */", payload)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wiki", type=Path, help="directory containing the published index.md and topic pages")
    args = parser.parse_args()
    output = args.wiki / "wiki-map.html"
    try:
        output.write_text(render_wiki(args.wiki), encoding="utf-8")
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(output)


HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Memory wiki map</title>
<style>
:root{color-scheme:light;--paper:#f6f3eb;--ink:#172b25;--green:#1b5045;--edge:#c4c9bb;--pale:#e1ebe1;--muted:#53655b}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.5 system-ui,sans-serif}
main{max-width:1320px;margin:auto;padding:32px 36px}
h1,h2{font-family:Georgia,serif;line-height:1.1;margin:0}
h1{font-size:clamp(34px,5vw,59px)}
h2{font-size:27px}
.eyebrow,.counts,code{font:12px/1.4 ui-monospace,monospace}
.eyebrow{color:var(--green);letter-spacing:.12em;text-transform:uppercase}
header{padding-bottom:18px;border-bottom:1px solid var(--edge)}
.counts{color:var(--muted);margin:10px 0 0}
.layout{display:grid;grid-template-columns:minmax(0,2fr) minmax(280px,1fr);gap:22px;margin-top:20px}
.graph,.detail{background:#fffdf7;border:1px solid var(--edge);min-width:0}
.graph{padding:10px}
.graph p{margin:4px 10px 8px;color:var(--muted)}
svg{display:block;width:100%;height:auto}
.edge{stroke:#a9b5a7;stroke-width:1.1;opacity:.6}
.edge.index{stroke-dasharray:4 5;opacity:.4}
.edge.active{stroke:var(--green);stroke-width:2.4;opacity:1}
.node{cursor:pointer;color:var(--ink)}
.node rect{fill:#fffdf7;stroke:#82968a;stroke-width:1.3}
.node text{fill:currentColor;text-anchor:middle;font:600 14px system-ui,sans-serif;pointer-events:none}
.node.neighbor rect{fill:var(--pale)}
.node.selected{color:white}
.node.selected rect{fill:var(--green);stroke:var(--green)}
.node:focus-visible rect{stroke:#a15121;stroke-width:3}
.detail{padding:18px}
.detail code{display:block;color:var(--muted);margin:6px 0 12px;overflow-wrap:anywhere}
#body{font:14px/1.55 system-ui,sans-serif;white-space:pre-wrap;overflow-wrap:anywhere}
.page-link{display:inline;padding:0;border:0;background:none;text-decoration:underline}
.jump{display:flex;flex-wrap:wrap;gap:6px;margin-top:12px}
button{background:var(--pale);color:var(--green);border:1px solid var(--edge);border-radius:3px;padding:5px 8px;cursor:pointer;font:inherit;text-align:left}
button:focus-visible{outline:2px solid var(--green);outline-offset:2px}
@media(max-width:760px){main{padding:20px 14px}.layout{grid-template-columns:1fr}.graph{overflow-x:auto}.graph svg{min-width:540px}}
</style>
</head>
<body>
<main>
  <header><p class="eyebrow">Field Notes · Memory wiki</p><h1 id="title"></h1><p class="counts" id="counts"></p></header>
  <div class="layout">
    <section class="graph" aria-label="Page network">
      <svg id="network" aria-label="Select a page to read it"></svg>
      <p>Lines show links in the Markdown. Dashed lines lead from the index.</p>
    </section>
    <section class="detail" aria-label="Selected page">
      <h2 id="page-title"></h2><code id="path"></code><div id="body"></div>
      <div class="jump" id="neighbors" aria-label="Linked pages"></div>
    </section>
  </div>
</main>
<script>
const {pages, edges} = /* WIKI_DATA */;
const index = 'index.md';
const topics = Object.keys(pages).filter(path => path !== index);
const network = document.querySelector('#network');
const radius = Math.max(235, topics.length * 25);
const center = radius + 86;
network.setAttribute('viewBox', '0 0 ' + (2 * center) + ' ' + (2 * center - 60));
const points = new Map([[index, [center, center - 30]]]);
topics.forEach((path, i) => {
  const angle = (2 * Math.PI * i / topics.length) - Math.PI / 2;
  points.set(path, [center + radius * Math.cos(angle), center - 30 + (radius - 35) * Math.sin(angle)]);
});
document.querySelector('#title').textContent = pages[index].title;
document.querySelector('#counts').textContent = topics.length + ' topic pages · ' + edges.length + ' page connections';

function svgElement(tag, attributes) {
  const element = document.createElementNS('http://www.w3.org/2000/svg', tag);
  for (const [key, value] of Object.entries(attributes)) element.setAttribute(key, value);
  return element;
}

const lines = edges.map(([from, to]) => {
  const [x1, y1] = points.get(from);
  const [x2, y2] = points.get(to);
  const line = svgElement('line', {x1, y1, x2, y2, class: from === index || to === index ? 'edge index' : 'edge'});
  network.append(line);
  return line;
});
const nodes = new Map();
for (const [path, [x, y]] of points) {
  const group = svgElement('g', {class: 'node', transform: 'translate(' + x + ' ' + y + ')', tabindex: '0', role: 'button', 'aria-label': pages[path].title});
  const label = svgElement('text', {});
  const words = pages[path].title.split(/\s+/);
  const rows = [''];
  for (const word of words) {
    const last = rows.length - 1;
    if (rows[last] && (rows[last] + ' ' + word).length > 17) rows.push(word);
    else rows[last] = (rows[last] + ' ' + word).trim();
  }
  rows.forEach((row, i) => {
    const span = svgElement('tspan', {x: 0, y: 5 + (i - (rows.length - 1) / 2) * 17});
    span.textContent = row;
    label.append(span);
  });
  const height = Math.max(38, rows.length * 17 + 13);
  group.append(svgElement('rect', {x: -71, y: -height / 2, width: 142, height, rx: 8}), label);
  group.addEventListener('click', () => select(path));
  group.addEventListener('keydown', event => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      select(path);
    }
  });
  network.append(group);
  nodes.set(path, group);
}

function openPage(file) {
  select(file);
  nodes.get(file).focus();
}

function renderBody(page) {
  const container = document.querySelector('#body');
  const body = page.body.replace(/^#\s+[^\n]+\n*/, '').trim();
  container.replaceChildren();
  let offset = 0;
  for (const match of body.matchAll(/(?<!!)\[([^\]\n]+)\]\(([^)\s]+)\)/g)) {
    container.append(body.slice(offset, match.index));
    const [, label, href] = match;
    if (Object.hasOwn(page.links, href)) {
      const button = document.createElement('button');
      button.className = 'page-link';
      button.textContent = label;
      button.onclick = () => openPage(page.links[href]);
      container.append(button);
    } else {
      container.append(label);
    }
    offset = match.index + match[0].length;
  }
  container.append(body.slice(offset));
}

function select(path) {
  const related = new Set();
  edges.forEach(([from, to], i) => {
    const active = from === path || to === path;
    lines[i].classList.toggle('active', active);
    if (active) related.add(from === path ? to : from);
  });
  for (const [file, node] of nodes) {
    node.classList.toggle('selected', file === path);
    node.classList.toggle('neighbor', related.has(file));
    node.setAttribute('aria-pressed', String(file === path));
  }
  document.querySelector('#page-title').textContent = pages[path].title;
  document.querySelector('#path').textContent = path;
  renderBody(pages[path]);
  document.querySelector('#neighbors').replaceChildren(...[...related].map(file => {
    const button = document.createElement('button');
    button.textContent = pages[file].title;
    button.onclick = () => openPage(file);
    return button;
  }));
}
select(index);
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
