# Linux，自底向上

从硬件与进程，到文件系统、容器、虚拟化与系统生态。面向有软件背景、希望真正理解原理而不过度陷入实现细节的读者。

第 1.1 版（独立交叉审稿修订） · 资料核查基准日 2026-10-22。

本版包含导读、20 章正文、2 篇附录、20 幅原创机制图与 1 幅 AI 封面概念插画；正文及附录约 4.6 万汉字，148 个去重来源。关键事实在相邻位置链接原始资料，社区研究、教学模型与未实测的推演明确区分。

## 阅读

阅读顺序由 [book.json](book.json) 管理。已打包版本可直接打开 `build/Linux-From-the-Ground-Up.epub`；也可在支持相对图片的 Markdown 阅读器中打开合订稿 `build/Linux-From-the-Ground-Up.md`。

分章从 [导读](chapters/00-preface.md) 开始。四个部分依次是：

1. 01–05：计算机、启动、进程、内存与二进制运行。
2. 06–09：VFS、存储、FUSE 与 OverlayFS。
3. 10–13：隔离、容器、KVM、QEMU 与跨架构。
4. 14–20：网络、eBPF、异步 I/O、桌面、诊断、Android、macOS、Switch 与综合案例。

来源见正文就近链接、各章末的边界说明，以及 [来源索引](references/index.md)。其他学习路线见 [附录 A](appendices/reading-and-glossary.md)。

## 构建与检查

依赖 Python 3、Git。构建 EPUB 另需 Pandoc、Inkscape 与 Python Pillow（用于逐图校验和完整解码）；SVG 图解生成仅用 Python 标准库。系统工具通过相应软件包管理器安装，Pillow 可用 `python3 -m pip install Pillow` 安装。

```sh
python3 scripts/build_book.py --check-only
python3 scripts/draw_diagrams.py
python3 scripts/build_book.py
```

第一条检查章节清单、标题一致性、相对资源、引用登记、代码围栏、SVG XML 及 Git 初始提交。第二条重新绘制精确机制图。第三条生成合订 Markdown、PNG 和 EPUB，并对每幅 PNG 及 EPUB 内嵌图片完整解码，产物放在 `build/`。不要求联网生成正文或插图，不重跑 AI 封面。

`chapters/` 是分章主稿，`appendices/` 放附录，`assets/images/` 是图片源，`references/` 是来源与核查记录。在线阅读站源码位于 `site/`，由 `scripts/build_site.py` 直接读取同一份章节清单与主稿，不另存一套正文。

## Git 与交付

根提交只包含零字节 README，后续逐步加入结构、分章、图解和构建工具。工程包额外含 `history.git.bundle`，用于恢复完整本地版本历史：

```sh
git clone history.git.bundle linux-book-with-history
```

远端仓库为 `https://github.com/YZYExp/Learn-Linux.git`。具体检查与未覆盖范围见 [核查记录](references/validation.md)。

第 1.1 版的独立审稿意见、证据和处理结果见 [交叉审稿记录](references/reviews/summary.md)。


## GitHub Pages

发布目标：`YZYExp/Learn-Linux`。首页、分章阅读、原始资料、审稿记录、全文搜索、深浅主题和 EPUB 下载由同一套源文件构建。

```sh
python3 -m pip install -r site/requirements.txt
python3 scripts/build_site.py --base-path /Learn-Linux/
```

输出为 `build/site/`；本地从域名根目录预览时，可将 `--base-path` 改为 `/`。图解使用原始 SVG，保持完整比例，正文中可打开原图。

网页发布与整书导出独立运行：

- `.github/workflows/pages.yml`：推送 main 时发布页面，拉取请求做构建检查。只安装 Markdown 和 Pillow，不运行 apt，也不安装 Pandoc、Inkscape 或字体。保留章节、引用、SVG、根提交及网页本地链接检查。
- `.github/workflows/build-book.yml`：书稿、图源或导出工具变化时独立构建 EPUB，也可手动运行。此流程才安装 Pandoc、Inkscape、Noto CJK 字体，并完整解码检查 21 幅内嵌图片。成功后在该次运行的 Artifacts 中下载 `linux-book` 压缩包；网站的“EPUB 构建与下载”链接指向此流程。整书导出失败不会阻塞网页发布。

本地如需在网站中附带已构建的 EPUB，可显式传入文件，构建器会先校验再复制；未传入时不依赖本地残留产物：

```sh
python3 scripts/build_book.py
python3 scripts/build_site.py --base-path /Learn-Linux/ --epub build/Linux-From-the-Ground-Up.epub
```

Actions artifact 下载需要登录 GitHub。网页阅读无需登录。

首次发布需要在仓库 Settings → Pages → Build and deployment 中将 Source 选为 **GitHub Actions**。工作流不内置访问令牌，也不通过扩大仓库访问权限来替代这一设置；启用后重新运行即可部署。

审稿版书稿与来源沿用原有逐步提交。若通过 GitHub API 同步历史，提交内容和顺序可保持一致，但提交 SHA 与创建时间会由远端重新生成。
