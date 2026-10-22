# 图像说明

## 封面

`assets/images/cover.png`：AI 生成概念插画，用于表达从硬件到系统生态的学习方向，不能据此判断实际内核组件、接口关系或硬件结构。已逐张查看生成结果并纳入书稿与 EPUB 封面。内置 imagegen 生成，无外部摄影作品拼贴。

生成提示词：

> Use case: stylized-concept. Asset type: cover illustration for a Chinese technical book explaining Linux from hardware upward. Create a sophisticated editorial illustration, portrait 2:3. An elegant cutaway miniature computing city built as four floating physical strata: lowest silicon board and copper traces, above subtle dark blue kernel hub, above organized translucent workspaces, at top flourishing small abstract applications and bridges. Use this strictly as an imaginative metaphor, NOT an exact technical diagram. Precise isometric architectural draftsmanship with tactile paper and brushed metal, warm ivory background, midnight blue, muted teal and tiny warm orange accents. Calm, intelligent, beautiful, restrained composition, abundant breathing space. One tiny curious penguin at lower corner as scale cue. No logos, no random code, no text, no lettering, no arrows. The upper quarter is mostly ivory negative space for separately typeset title. High visual quality print book art.

## 机制图

`assets/images/01-map.svg` 至 `20-capstone.svg` 是原创程序绘制机制示意，生成脚本为 `scripts/draw_diagrams.py`。内容依据对应章节资料与教学模型组织，非外部原图转载。机制图不使用生图代替精确结构；20 张均已渲染并检查文字与布局。EPUB 采用这些 SVG 导出的 PNG，以兼容不同阅读器；原始 SVG 保留在工程中。
