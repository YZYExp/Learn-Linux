# Linux，自底向上

从硬件与进程，到文件系统、容器、虚拟化与系统生态。面向有软件背景、希望真正理解原理而不过度陷入实现细节的读者。

第 1.0 版 · 资料核查基准日 2026-10-22。

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

依赖 Python 3、Git。构建 EPUB 另需 Pandoc、Inkscape；SVG 图解生成仅用 Python 标准库。不同系统请通过自己的软件包管理器安装这些工具。

```sh
python3 scripts/build_book.py --check-only
python3 scripts/draw_diagrams.py
python3 scripts/build_book.py
```

第一条检查章节清单、相对资源、引用登记、代码围栏、SVG XML 及 Git 初始提交。第二条重新绘制精确机制图。第三条生成合订 Markdown、PNG 和 EPUB，产物放在 `build/`。不要求联网生成正文或插图，不重跑 AI 封面。

`chapters/` 是分章主稿，`appendices/` 放附录，`assets/images/` 是图片源，`references/` 是来源与核查记录。后续 Home Page 源码预留为 `site/`，直接读取同一份章节清单与主稿；本版未生成或部署网站。

## Git 与交付

根提交只包含零字节 README，后续逐步加入结构、分章、图解和构建工具。工程包额外含 `history.git.bundle`，用于恢复完整本地版本历史：

```sh
git clone history.git.bundle linux-book-with-history
```

未指定远端，也未推送到任何旧书仓库。具体检查与未覆盖范围见 [核查记录](references/validation.md)。
