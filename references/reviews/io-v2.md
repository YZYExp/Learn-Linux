# 第二轮独立交叉审稿：文件、I/O、网络与内核扩展

审稿日期：2026-10-22。审稿对象：本次从当前工程包取得的第 06、07、08、09、14、15 章及同号 SVG。

## 结论

六章正文已逐节读完，六幅 SVG 的节点、图注与连线源码均已检查；本轮没有发现可确证的高、中严重度技术错误，也没有发现需要以勘误方式处理的低严重度事实错误。未修改正文或图解。下文列出核对点与可选增补，不能将“未发现”解释为对所有版本和实现的无条件认证。

本轮重新打开并核对了 26 个原始资料入口中的相关段落；没有只检查 URL 是否存在。各章实际引用 URL 与项目来源登记的对应检查通过。长文档按所核对命题读取重点段落，不声称逐字审计了所有文档及实现源码。

## 重点复核记录

| 章节与位置 | 核对命题 | 原始来源及支持点 | 判断 |
| --- | --- | --- | --- |
| 06，一个整数为什么能代表文件 | 独立 open 的打开状态与 dup 共享状态不同；fd 标志与状态标志分层 | [open(2)](https://man7.org/linux/man-pages/man2/open.2.html)、[dup(2)](https://man7.org/linux/man-pages/man2/dup.2.html)：fd 引用 open file description，dup 共享偏移和文件状态 | 正确，图解未把 fd 编号当文件全局身份 |
| 06，删除的是名字 | unlink 移除名称；已有打开引用允许继续使用 | [unlink(2)](https://man7.org/linux/man-pages/man2/unlink.2.html)：最后链接删除后，仍打开的文件保持存在 | 正确，未将某次磁盘占用归为唯一原因 |
| 06，从字符串到对象 | dentry、inode 与并发路径查找不是同一个对象或瞬时稳定关系 | [Pathname lookup](https://docs.kernel.org/filesystems/path-lookup.html)：名字、目录、缓存及并发条件的分层 | 正确，正文明确缓存不等于磁盘目录记录 |
| 07，fsync 同步的是什么 | 文件同步、目录项持久化与路径替换原子性分开 | [fsync(2)](https://man7.org/linux/man-pages/man2/fsync.2.html)：文件同步不必然使父目录项落盘，需要目录同步 | 正确，没有把 rename 描述为断电事务 |
| 07，日志与写时复制 | ext4 默认不将全部用户数据记入日志 | [ext4 Journal](https://docs.kernel.org/filesystems/ext4/journal.html)：默认元数据日志及各数据模式的不同保证 | 正确，未承诺最后一次保存必然完整 |
| 08，缓存模式 | direct I/O 绕过页缓存；writeback-cache 有统一修改路径假设 | [FUSE I/O Modes](https://docs.kernel.org/filesystems/fuse/fuse-io.html)：缓存模式及外部修改限制 | 正确，网络后端适用前提已保留 |
| 08，回调语义 | flush、release、fsync 不能混为同一持久性操作 | [libfuse fuse_operations](https://libfuse.github.io/doxygen/structfuse__operations.html)：flush 与 close 相关且可重复，release 对应最终引用释放，flush 不等于 fsync | 正确，表述没有要求一次 open 只能有一次 flush |
| 08，权限与故障 | allow_other、default_permissions 与后端鉴权职责不同 | [FUSE Overview](https://docs.kernel.org/filesystems/fuse/fuse.html)：挂载选项、请求等待及连接中止 | 正确，没有给出默认特权操作 |
| 08，virtiofs | 复用 FUSE 协议并更换传输边界 | [virtiofs 内部机制](https://docs.kernel.org/filesystems/virtiofs.html)：客户机为客户端，virtqueue 承载请求与响应；[项目概览](https://virtio-fs.gitlab.io/) | 正确，没有将它画成一般网络文件系统 |
| 08，SSHFS 案例 | SFTP 路线与项目维护说明 | [SSHFS README](https://github.com/libfuse/sshfs)：Development Status 与 About | 与核查时公开说明一致，日期条件已注明 |
| 09，层目录和修改 | work 与 upper 同文件系统，目录可合并，元数据复制及重命名有条件 | [OverlayFS](https://docs.kernel.org/filesystems/overlayfs.html)：Directories、Metadata only copy up、Renaming directories | 正确，正文与图09一致 |
| 09，whiteout | OCI 归档删除表示与内核 OverlayFS 表示不同 | [OCI layer.md](https://github.com/opencontainers/image-spec/blob/main/layer.md)：.wh. 与 opaque 标记；[OverlayFS](https://docs.kernel.org/filesystems/overlayfs.html)：内核 whiteout 语义 | 正确，未把 tar 特殊名称直接当磁盘内部表示 |
| 09，Docker 存储范围 | classic overlay2 与 containerd snapshotter 区分 | [Docker OverlayFS storage driver](https://docs.docker.com/engine/storage/drivers/overlayfs-driver/)：页面适用范围及 copy-up | 正确，未外推默认后端 |
| 14，通信语义 | TCP 字节流无消息边界；UDP 可 connect 且保留报文 | [tcp(7)](https://man7.org/linux/man-pages/man7/tcp.7.html)、[udp(7)](https://man7.org/linux/man-pages/man7/udp.7.html) | 正确，没有将 transport 成功与业务成功混淆 |
| 14，网络视图 | 网络命名空间隔离设备、路由与端口等资源 | [network_namespaces(7)](https://man7.org/linux/man-pages/man7/network_namespaces.7.html) | 正确，并对共享网络视图保留例外 |
| 14，连接与转发 | bridge 的二层转发与有状态 NAT 的地址转换分工 | [Ethernet Bridging](https://docs.kernel.org/networking/bridge.html)、[nftables NAT](https://wiki.nftables.org/wiki-nftables/index.php/Performing_Network_Address_Translation_%28NAT%29) | 正确，没有将 NAT 当作身份认证 |
| 15，eBPF 检查与移植 | verifier、BTF、CO-RE 和功能存在性相互独立 | [verifier](https://docs.kernel.org/bpf/verifier.html)、[BTF](https://docs.kernel.org/bpf/btf.html)、[libbpf](https://docs.kernel.org/bpf/libbpf/libbpf_overview.html) | 正确，正文避免套用旧版循环限制，也没有承诺补出新 helper |
| 15，io_uring 与 epoll | 共享队列提交/结果，与 fd 就绪通知不同 | [io_uring(7)](https://man7.org/linux/man-pages/man7/io_uring.7.html)、[epoll(7)](https://man7.org/linux/man-pages/man7/epoll.7.html) | 核心对照正确；图15两面板没有串接 |
| 15，bpftrace | 探针、条件与动作的组织方式 | [bpftrace Language 0.24](https://bpftrace.org/docs/release_024/language) | 有版本限定的原始来源支持 |

## 可选增补，不计为勘误

### IO-OPT-01：io_uring 请求与完成条目并非总是一对一

- 级别：可选教学补充。
- 位置：第15章“io_uring 把请求与完成分开”。
- 原文短引：“应用用自身标记把完成记录与请求对应。”
- 现文没有声称严格一对一，因此不构成错误。但若今后扩写生命周期，建议补一句：多次完成请求可能产生多个 CQE，应用需依据标志判断后续完成，而非收到第一条就释放资源。
- 证据：[io_uring(7)](https://man7.org/linux/man-pages/man7/io_uring.7.html)，IORING_CQE_F_MORE 明确说明同一请求仍可能有后续完成。无需把本章扩写成完整 API 手册。

### IO-OPT-02：关闭 fd 与撤销映射是不同的引用释放动作

- 级别：可选跨章衔接。
- 位置：第06章“删除的是名字”与第08章回调段。
- 原文短引：“等这些打开引用结束后，相关空间才有机会被回收。”
- “有机会”已避免无条件回收保证，不计为事实错误。可加一个指向内存章的短句，提示文件映射也可以保持相应引用，关闭某个 fd 不等于所有引用都消失。
- 证据：[libfuse fuse_operations](https://libfuse.github.io/doxygen/structfuse__operations.html)，release 条件明确包括 fd 关闭与映射撤销；不建议只根据 fd 清单断言对象可回收。

## 实际边界

没有执行特权挂载、网络配置、eBPF 装载、断电实验或性能基准，也没有对内核实现作完整源码审计。检查图解采用 SVG XML 结构与语义对应，不把它冒充本轮重新逐幅视觉排版验收。结论限于这些章节当前陈述的机制与已注明条件。
