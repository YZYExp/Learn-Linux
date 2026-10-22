import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
titles = [
('00-preface', '导读：学会沿着边界追问'),
('01-map', '计算机、内核与发行版：先建立地图'),
('02-boot', '从通电到服务：系统怎样活过来'),
('03-process', '进程与线程：谁在运行，谁在等待'),
('04-memory', '内存：地址是一份受管理的承诺'),
('05-abi', '程序怎样运行：从 ELF 到系统调用'),
('06-vfs', '文件：名字、对象与打开的关系'),
('07-storage', '存储：写成功以后，数据在哪里'),
('08-fuse', 'FUSE：把文件系统的实现搬到用户态'),
('09-overlayfs', 'OverlayFS：怎样把多层目录读成一层'),
('10-isolation', '隔离、预算与权限：三个不同的问题'),
('11-containers', '容器：把内核机制组装成运行环境'),
('12-kvm', 'KVM：让 Linux 管理另一台机器的执行'),
('13-qemu', 'QEMU：模拟、虚拟化与跨架构的边界'),
('14-network', '网络：从一个 socket 到另一端'),
('15-ebpf', 'eBPF 与异步 I/O：扩展观察与提交方式'),
('16-devices-desktop', '驱动与桌面：屏幕背后的协作'),
('17-observability', '可观测性：把慢与失败变成可检验的问题'),
('18-android', 'Android：同一内核上长出的另一套平台'),
('19-families', 'macOS 与 Switch：相似概念，不同系统'),
('20-capstone', '贯通全书：在 Mac 上追踪一个 Linux 服务'),
]
book = {'title':'Linux，自底向上', 'subtitle':'从硬件与进程，到文件系统、容器、虚拟化与系统生态',
 'language':'zh-CN', 'edition':'1.1', 'date':'2026-10-22',
 'description':'面向已有软件背景读者的图解原理读本，以机制、边界与可核查来源组织知识。',
 'cover':'assets/images/cover.png', 'chapters':[
 {'id':slug.split('-')[0], 'title':title, 'order':n, 'source':f'chapters/{slug}.md', 'slug':slug}
 for n,(slug,title) in enumerate(titles)],
 'appendices':[{'title':'阅读路线与术语索引','source':'appendices/reading-and-glossary.md'},
 {'title':'引用规范与适用边界','source':'appendices/evidence-policy.md'}],
 'site':{'source_directory':'site','implemented':False,'content_source':'book.json'}}
(ROOT/'book.json').write_text(json.dumps(book, ensure_ascii=False, indent=2)+'\n')
