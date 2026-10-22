"""Draw the seven expansion diagrams using only Python's standard library.

Each drawing is a teaching model, not a measured trace. Text remains SVG text.
Run from any directory: python scripts/draw_expansion_diagrams.py
"""
from pathlib import Path
from html import escape
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/images'
NAVY, TEAL, ORANGE = '#19364a', '#157d7b', '#cd713e'
BG, LINE, MUTED = '#f7f5ef', '#aebbbd', '#5a6c75'
GREEN, BLUE, WARM = '#e5f1ed', '#e9eef5', '#f7e9df'

class Drawing:
    def __init__(self, title, subtitle, height=1200):
        self.height = height
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="{height}" viewBox="0 0 800 {height}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{escape(title)}</title><desc id="desc">{escape(subtitle)}。原创教学示意，非实际时序或性能测量。</desc>',
            '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="#157d7b"/></marker><marker id="orange" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="#cd713e"/></marker></defs>',
            f'<rect width="800" height="{height}" fill="{BG}"/>',
            '<style>text{font-family:"Noto Sans CJK SC","Noto Sans SC",sans-serif}</style>']
        self.text(44, 55, title, 29, bold=True)
        self.text(44, 91, subtitle, 20, MUTED)
        self.parts.append(f'<path d="M44 116H756" stroke="{LINE}"/>')
    def text(self, x, y, text, size=22, color=NAVY, bold=False, anchor='start'):
        self.parts.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{700 if bold else 400}" text-anchor="{anchor}">{escape(text)}</text>')
    def box(self, y, title, lines=(), fill='white', x=60, w=680, h=None, label=None):
        h = h or (73 + 32 * len(lines))
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="{fill}" stroke="{LINE}" stroke-width="1.5"/>')
        if label:
            self.text(x+22, y+32, label, 18, TEAL, True)
            ty=y+68
        else:
            ty=y+37
        self.text(x+22, ty, title, 25, bold=True)
        for i, line in enumerate(lines): self.text(x+22, ty+35+32*i, line, 21, MUTED)
        return y+h
    def arrow(self, x1, y1, x2, y2, label=None, orange=False):
        color = ORANGE if orange else TEAL
        self.parts.append(f'<path d="M{x1} {y1}L{x2} {y2}" fill="none" stroke="{color}" stroke-width="2.6" marker-end="url(#{"orange" if orange else "arrow"})"/>')
        if label: self.text(x1+16, (y1+y2)/2+6, label, 19, color)
    def path(self, points, orange=False, dashed=False):
        color=ORANGE if orange else TEAL
        self.parts.append(f'<path d="{points}" fill="none" stroke="{color}" stroke-width="2.6" marker-end="url(#{"orange" if orange else "arrow"})"'+(' stroke-dasharray="7 6"' if dashed else '')+'/>')
    def note(self, y, lines, fill=GREEN):
        self.box(y, '读图边界', lines, fill, h=74+32*len(lines))
    def save(self, slug, footer='原创机制示意 · 箭头表示关系或可能路径，并非完整执行轨迹'):
        self.text(44, self.height-28, footer, 17, MUTED)
        self.parts.append('</svg>')
        content='\n'.join(self.parts)+'\n'
        ET.fromstring(content)
        (OUT/(slug+'.svg')).write_text(content)


def concurrency():
    d=Drawing('并发：保护数据，也要组织等待', '以一个使用 futex 的互斥实现为教学模型', 1370)
    d.box(145,'共享队列：锁保护的是不变量', ['例：长度、头尾指针与节点关系要一起保持正确。', '一次原子更新，不等于整个复合操作受保护。'], BLUE, h=145)
    d.arrow(400,290,400,340)
    d.box(340,'① 用户态尝试获取锁', ['原子操作参与竞争；无争用路径可留在用户态。'],GREEN,h=115)
    d.text(80,493,'成功 → 进入临界区',21,TEAL,True)
    d.text(430,493,'竞争失败 ↓',21,ORANGE,True)
    d.arrow(585,505,585,544,orange=True)
    d.box(544,'② FUTEX_WAIT：比较，再决定是否等待', ['内核检查 futex 字是否仍等于预期值；', '值已变化可立即返回，并非一定进入睡眠。'], WARM, h=145)
    d.arrow(400,689,400,738,'可能阻塞')
    d.box(738,'③ 持有者更新状态，按协议唤醒', ['FUTEX_WAKE 使等待者有机会重新运行；', '唤醒不等于把锁授予某个等待者。'], BLUE,h=145)
    d.arrow(400,883,400,932)
    d.box(932,'④ 再检查状态，再参与竞争', ['等待返回后仍须遵守锁／条件的完整协议。', 'futex 提供等待原语，锁语义由实现组织。'],GREEN,h=145)
    d.path('M60 1000H28V398H58',dashed=True)
    d.note(1115,['不展示具体库的所有状态、内存序或公平性策略。', 'CPU 缓存一致性不能替代语言层的同步规则。'])
    d.save('21-concurrency')


def distributions():
    d=Drawing('发行版：把软件组织成可维护的系统', '包文件、仓库元数据与应用数据各有边界', 1260)
    d.box(145,'① 仓库提供候选版本与元数据', ['包名、版本、依赖关系与来源信息。', '验证可信元数据，再按其记录核查包内容。'], BLUE,h=145)
    d.arrow(400,290,400,340)
    d.box(340,'② 包管理器解析系统变化', ['结合已安装状态，选择安装、升级或移除方案。', '依赖满足并不证明应用行为一定兼容。'],GREEN,h=145)
    d.arrow(400,485,400,535)
    d.box(535,'③ 执行安装事务与配置动作', ['部署文件，更新包数据库；可能运行维护脚本。', '具体的原子性与恢复能力依实现而不同。'],BLUE,h=145)
    d.arrow(235,680,235,740)
    d.arrow(565,680,565,740)
    d.box(740,'系统软件', ['可追踪包与版本。', '部分方案支持', '切换系统代际。'],GREEN,x=60,w=325,h=180)
    d.box(740,'应用数据', ['数据库、用户文件。', '运行中的写入与迁移', '通常另需备份策略。'],WARM,x=415,w=325,h=180)
    d.note(966,['回滚软件版本，不自动撤销数据库迁移或用户写入。', 'Nix 的代际切换与传统原地安装不是同一种机制。', '签名与哈希验证说明来源／完整性，不保证没有缺陷。'])
    d.save('22-distributions')


def topology():
    d=Drawing('硬件拓扑：同一地址空间，不同访问路径', 'NUMA 局部性与设备 DMA 是两组相关但不同的问题', 1320)
    d.box(145,'NUMA 节点 A', ['CPU／缓存', '本地内存'],BLUE,x=60,w=325,h=155)
    d.box(145,'NUMA 节点 B', ['CPU／缓存', '本地内存'],GREEN,x=415,w=325,h=155)
    d.path('M385 224H413')
    d.text(400,337,'节点间互连：访问远端内存仍有路径与代价',20,MUTED,anchor='middle')
    d.box(383,'布局问题：放置线程，也要考虑页在哪里', ['页的实际放置受内存策略、分配时机等影响。', '把线程绑到某个 CPU，不会自动迁移所有数据。'],GREEN,h=145)
    d.parts.append(f'<path d="M60 548H740" stroke="{LINE}" stroke-dasharray="6 6"/>')
    d.box(578,'DMA 路径 1：设备发起请求', ['驱动使用 DMA API 获得设备可用的地址。', '该地址不能直接当作 CPU 虚拟地址。'],BLUE,h=145)
    d.arrow(400,723,400,773,'若该平台与设备启用地址翻译')
    d.box(773,'DMA 路径 2：IOMMU 翻译与访问控制', ['把设备侧地址映射到允许访问的内存范围。', '映射本身不替代同步、所有权和生命周期管理。'],WARM,h=145)
    d.arrow(400,918,400,968)
    d.box(968,'DMA 路径 3：访问内存，按协议接手', ['缓存是否一致、是否要显式同步，依平台与映射而定。', '设备所在节点也会影响访问的局部性。'],GREEN,h=145)
    d.text(60,1170,'边界：并非每台机器都有多个 NUMA 节点或启用 IOMMU。',19,MUTED)
    d.text(60,1203,'示意未画出 PCIe、所有缓存层及总线实际连接。',19,MUTED)
    d.save('23-topology')


def container():
    d=Drawing('案例一：从镜像到一个容器服务', '镜像内容、进程环境、网络与持久化分别组装', 1320)
    d.box(145,'① 镜像提供文件内容', ['镜像层描述根文件系统变化；不是运行中的进程。', '常见 Linux 存储路径可用 OverlayFS 合并层。'],BLUE,h=145)
    d.arrow(400,290,400,340)
    d.box(340,'② 运行时准备执行环境', ['挂载根目录与所需文件系统，设置资源视图。', 'namespace、cgroup、权限配置各自承担不同职责。'],GREEN,h=145)
    d.arrow(400,485,400,535)
    d.box(535,'③ 启动 Linux 进程', ['进程使用宿主 Linux 内核执行系统调用。', '应用仍需要库、配置、凭据与可访问的数据。'],BLUE,h=145)
    d.arrow(235,680,235,735)
    d.arrow(565,680,565,735)
    d.box(735,'网络连接', ['接口与路由', '端口发布／转发', '取决于网络方案'],GREEN,x=60,w=325,h=180)
    d.box(735,'持久化连接', ['卷或绑定挂载', '权限与文件语义', '独立于可写容器层'],WARM,x=415,w=325,h=180)
    d.note(965,['这是常见 Linux 容器的组织模型，不是唯一启动时序。', '镜像层不强制要求 OverlayFS；网络也不必使用网桥。', '在 macOS 上运行时，Linux 内核通常位于虚拟机中。'])
    d.save('case-01-container')


def transaction():
    d=Drawing('案例二：事务确认与数据页回写', '以 PostgreSQL 的 WAL 思路区分两条持久化路径', 1370)
    d.box(145,'① 事务改变数据库状态', ['内存中的数据页变脏，并产生 WAL 记录。', 'WAL 先行原则约束相关记录与数据页的落盘顺序。'],BLUE,h=145)
    d.arrow(400,290,400,340)
    d.box(340,'② 提交等待相关 WAL 达到要求的位置', ['默认同步提交需要等待本地 WAL 刷入持久存储；', '同步复制配置还可能加入远端等待。'],GREEN,h=145)
    d.arrow(400,485,400,535)
    d.box(535,'③ 系统调用经过 OS 与存储栈', ['普通写入成功不等于掉电后可恢复。', '同步要求仍依赖设备、缓存与存储栈正确兑现。'],WARM,h=145)
    d.arrow(400,680,400,730)
    d.box(730,'④ 达到提交配置要求，向客户端确认', ['不要求每个被修改的数据页都已写入数据文件。'],GREEN,h=115)
    d.arrow(400,845,400,895,'另一条持续进行的工作')
    d.box(895,'⑤ 后台写页与检查点推进', ['在 WAL 顺序约束下写出脏页，并推进恢复起点。', '崩溃恢复可以重放所需 WAL。'],BLUE,h=145)
    d.note(1088,['图中编号帮助理解依赖，不代表后台工作等到确认后才开始。', '关闭同步、异步提交或更改复制配置，会改变确认保证。', '未提供设备故障实验，也不覆盖所有数据库实现。'])
    d.save('case-02-transaction')


def vm():
    d=Drawing('案例三：虚拟机的执行路径与 I/O 路径', '一个客户机中，CPU 执行与设备请求由不同机制协作', 1370)
    d.box(145,'① QEMU 建立机器模型', ['准备客户机内存、虚拟设备与 vCPU 执行上下文。', '使用 KVM 时，客户机执行由内核接口配合硬件加速。'],BLUE,h=145)
    d.arrow(400,290,400,340)
    d.box(340,'② 客户机运行应用与内核', ['客户机的系统调用首先进入客户机内核。', '不是每次客户机系统调用都会退出到 QEMU。'],GREEN,h=145)
    d.arrow(235,485,235,545)
    d.arrow(565,485,565,545)
    d.box(545,'vCPU 执行', ['KVM_RUN 进入运行', '需要处理的退出事件', '交给相应处理路径'],BLUE,x=60,w=325,h=180)
    d.box(545,'virtio 请求', ['客户机驱动组织请求', '通过 virtqueue 协作', '通知设备后端'],GREEN,x=415,w=325,h=180)
    d.arrow(565,725,565,785)
    d.box(785,'③ 后端访问宿主资源', ['设备后端可能在 QEMU、内核 vhost 或其他进程中。', '块设备与网络后端再连接相应宿主 I/O 路径。'],WARM,h=145)
    d.arrow(400,930,400,980)
    d.box(980,'④ 完成信息回到客户机', ['后端更新队列状态；按设备与协商机制通知客户机。', '客户机驱动处理完成，应用随后获得结果。'],GREEN,h=145)
    d.text(60,1180,'边界：简化为常见 KVM＋virtio 组合，未画出所有退出原因。',19,MUTED)
    d.text(60,1213,'virtqueue 不是“把所有数据复制一次”的统一规定。',19,MUTED)
    d.save('case-03-virtual-machine')


def slow():
    d=Drawing('案例四：从服务变慢到可检验的解释', '先分开现象、证据与假设，再选择验证动作', 1320)
    d.box(145,'① 定义现象与发生范围', ['哪类请求变慢？尾延迟还是吞吐？从何时开始？', '记录负载、版本与资源限制等同时变化的条件。'],BLUE,h=145)
    d.arrow(400,290,400,340)
    d.box(340,'② 从多个方向收集证据', ['CPU：运行时间、可运行队列、配额节流。', '等待：锁竞争、存储／网络、资源压力与排队。'],GREEN,h=145)
    d.arrow(235,485,235,545)
    d.arrow(565,485,565,545)
    d.box(545,'观察信号', ['例如 CPU 利用率', 'I/O 延迟与 PSI', '应用请求追踪'],BLUE,x=60,w=325,h=180)
    d.box(545,'保留上下文', ['容器还是宿主范围？', '时间窗口是否一致？', '指标口径是否匹配？'],WARM,x=415,w=325,h=180)
    d.arrow(235,725,235,775)
    d.arrow(565,725,565,775)
    d.box(775,'③ 提出能被反驳的假设', ['例：请求等待 CPU 配额，而非“机器没有空闲核”。', '列出支持该假设的证据与能推翻它的结果。'],GREEN,h=145)
    d.arrow(400,920,400,970)
    d.box(970,'④ 在可控条件下验证并复查', ['一次改变一个关键条件，比较同口径的结果。', '记录不确定性，避免把相关性当作因果。'],BLUE,h=145)
    d.text(60,1175,'边界：PSI 表达资源停顿压力，单一指标不能独立证明根因。',19,MUTED)
    d.text(60,1208,'此图是诊断方法，不是已经完成的性能实验。',19,MUTED)
    d.save('case-04-slow-service')


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    for fn in (concurrency,distributions,topology,container,transaction,vm,slow):fn()
    print('Built and XML-validated 7 expansion SVG diagrams.')

if __name__ == '__main__':main()
