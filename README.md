# xskill.wiki

线上站点：[https://xskill.wiki](https://xskill.wiki)（`#start` 是新同学入口）。

这是产品站和文档站的源码。往 **`main`** 推送后，几秒内会同步到线上。

新同学请先看：[快速上手](https://xskill.wiki/#start) · [常用命令](https://xskill.wiki/wiki.html#features) · [怎么给文档补一页](https://xskill.wiki/wiki.html#contribute)

---

## 这是什么

xskill 会看你的编程助手（Claude Code、Codex、Cursor 等）平时怎么干活，把真正跑通的做法整理成技能文件（`SKILL.md`）。下次遇到同类问题，助手可以直接用，不用每次从零再推一遍。

一个人解决过的问题，可以变成全组都能用的技能。

支持三种运行方式：

1. **连公网实例（最快，免配大模型）**：
   ```bash
   pip install -U xskill
   xskill connect https://hub.xskill.wiki --token dd7f641c16ced6d1db43e754055fd2c8 --name 你的名字
   ```
2. **本机单机跑（数据不出机，自备大模型 Key）**：
   ```bash
   pip install -U xskill
   xskill serve   # 首次自动生成 ~/.xskill/config.yaml，填好 key 再跑一次即可
   ```
3. **自建团队服务器（团队私有共享）**：
   ```bash
   xskill serve --server                        # 服务器上启动，打印接入 token
   xskill connect <服务器IP:端口> --token <token> --name 你的名字  # 组员电脑连接
   ```

---

## 新同学先记住这五件事

| 你想做的事 | 用这个 |
| --- | --- |
| 用一句话，让系统马上写或改一条技能 | `xskill generate` |
| 手里已经有一份技能文件夹，想让同事搜到 | `xskill upload` |
| 把现成技能收进 xskill 自己的技能库，并装到助手里 | `xskill import` |
| 在共享库中按关键词查找技能，获取编号或直接试用 | `xskill search` |
| 直接改本机技能文件，改动自动传到服务器当草稿 | 手改即可，`connect` 常驻时会自动上传 |

这五件事的完整说明在 [Wiki · 常用命令](https://xskill.wiki/wiki.html#features)，源文件在 [`docs/features/`](docs/features/)。

和相近命令不要混：

- **upload** 是「放到共享目录，给人搜」。
- **import** 是「收进正式技能库，带版本，并装到助手里」。
- **search** 是「在共享库里按关键词查找技能与编号」。
- **generate** 是「你说话，服务器代写」。
- **手改自动上传** 不会立刻覆盖全队正式版，只作为下一轮自动改写的参考。

---

## 怎么给文档补一页（欢迎新同学）

发现某个命令网站上没写清楚？请直接补文档，不必先问。

1. 打开这个仓库：<https://github.com/SkillNerds/xskill-wiki>
2. 复制 [`docs/features/_template.md`](docs/features/_template.md)，改名为命令名，例如 `search.md`
3. 用白话写：一句话是什么、什么时候用、怎么敲、和相近命令的差别、要注意什么。**不要写只有内部才懂的词**；非写不可时，先用一句人话解释。
4. 在 `wiki.html` 的「常用命令」里加一小节，目录里加一条链接。
5. 在 `i18n.js` 里同时补 **英文** 和 **中文** 文案（命令本身不要翻译）。
6. 开 Pull Request，或有写权限就推到 `main`。`main` 会自动发到 <https://xskill.wiki>。

一篇合格的特性说明，大约一屏就能看完。范例：

- [`docs/features/generate.md`](docs/features/generate.md)
- [`docs/features/upload.md`](docs/features/upload.md)
- [`docs/features/import.md`](docs/features/import.md)
- [`docs/features/search.md`](docs/features/search.md)
- [`docs/features/rewrite-auto-upload.md`](docs/features/rewrite-auto-upload.md)

产品代码在 <https://github.com/SkillNerds/xskill>。文档仓库只放网站和说明。

---

## 本机开发这个网站

静态 HTML，没有构建步骤。用浏览器直接打开 `index.html`，或：

```bash
python3 -m http.server 8009 --bind 127.0.0.1 --directory .
```

改完推 `main` 即可上线。本机工作区有未提交改动时，自动同步会拒绝拉取，以免冲掉正在改的东西。

## Task graph architecture reference

`task-graph.html` is the bilingual public reference for Session, Atom, Task and
Attempt. The Wiki sidebar and Architecture section link to it. The site remains
static and needs no build step to serve.

Edit the paired sources in `docs/architecture/session-task-attempt.en.md` and
`docs/architecture/session-task-attempt.zh.md`. Keep the 13 sections aligned, then
regenerate the committed HTML with Python 3 and `Markdown==3.10.2` installed:

```sh
python3 scripts/render_task_graph_docs.py
python3 scripts/render_task_graph_docs.py --check
python3 scripts/check_task_graph_docs.py
```

The checker also uses Node to check the shared JavaScript syntax. Diagram sources
are the three `assets/task-graph-*.svg` files. Update both languages and diagrams
when behavior changes; the reference explicitly dates its implementation review.

For a local preview, serve this directory:

```sh
python3 -m http.server 8009 --bind 127.0.0.1
```

Then open `http://127.0.0.1:8009/task-graph.html`. Before publishing, check English
and Chinese at desktop and mobile widths, section links, diagram/table scrolling,
and the entry from `/wiki.html`.
