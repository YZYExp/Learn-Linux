# 第 22、23 章独立交叉审稿（1.2 扩展稿）

审稿日期：2026-10-22。审稿者未参与这两章原稿撰写；本轮只审阅和登记，没有修改正文。

## 结论与实际问题

在下述核查范围内，未发现需要修改的事实错误或引用失配，未提出阻断发布的问题。此结论表示所抽查的关键命题得到一手资料支持，不表示所有平台、配置或性能表现都已验证。

| 严重度 | 位置 | 实际问题 | 建议 |
| --- | --- | --- | --- |
| 无阻断项 | 第 22 章 22.3、22.5–22.6；第 23 章 23.3–23.5 | 未发现实际错误 | 保留现有条件与边界，不将原子回滚、首次访问分配、DMA coherent 或 IOMMU 隔离扩大成无条件保证 |

## 第 22 章：签名、环境切换与数据恢复

- **22.2，dpkg 数据库与维护脚本生成文件**：实际打开 `dpkg-query(1)`，其 `-L` 和 `-S` 说明均排除维护脚本额外创建的文件；正文没有把包数据库当成全盘快照，表述成立。核查：[Debian dpkg-query](https://manpages.debian.org/bookworm/dpkg/dpkg-query.1.en.html)。
- **22.3，APT 仓库签名**：实际打开 `apt-secure(8)`，核对归档信任链及“不做包级签名验证”的边界。正文区分签名 Release 元数据、索引／包校验和与独立开发者签名，并未把认证当成软件正确性证明，表述成立。核查：[Debian apt-secure](https://manpages.debian.org/bookworm/apt/apt-secure.8.en.html)。
- **22.4，安全修复回移与重启**：实际打开 Debian 安全 FAQ，核对其关于回移修复、检查完整版本及公告，以及更新后可能需要重启进程的说明。正文没有从上游版本号直接推断未修复，表述成立。核查：[Debian security FAQ](https://www.debian.org/security/faq)。
- **22.5，Nix generation 与原子范围**：实际打开 Nix 2.34 profiles 文档，核对包并存、用户环境及链接切换；正文限定为用户环境引用，不把它当成业务数据快照。另核对 derivation 的输入、执行环境和输出定义；正文区分构建输入记录与逐字节可复现性，未声称工具本身保证全部构建可复现。核查：[Profiles](https://nix.dev/manual/nix/2.34/package-management/profiles.html)、[Store Derivation](https://nix.dev/manual/nix/2.34/store/derivation/)。
- **22.6，OSTree 部署原子性与 `/var`**：实际打开 Atomic Upgrades 与 `/var` handling 文档，核对原子转换针对可启动部署列表，新部署准备与启动配置切换；`/var` 的持久可写状态不会随新部署普遍覆写。正文把数据库格式迁移作为教学假设，明确程序回退不等于数据恢复，表述成立。核查：[Atomic Upgrades](https://ostreedev.github.io/ostree/atomic-upgrades/)、[OSTree and /var](https://ostreedev.github.io/ostree/var/)。

## 第 23 章：NUMA、DMA 与 IOMMU

- **23.1、23.6，NUMA 距离与 `numa_maps`**：实际打开 `numa(7)` 和 `lscpu(1)`，核对相对位置影响访问时间、虚拟机输出通常反映客户机配置，以及 `N<node>=<nr_pages>` 统计当前映射页分布。正文没有把页分布当成访问计数或远端延迟，表述成立。核查：[numa(7)](https://man7.org/linux/man-pages/man7/numa.7.html)、[lscpu(1)](https://man7.org/linux/man-pages/man1/lscpu.1.html)。
- **23.3，默认策略与 first touch**：实际打开 NUMA Memory Policy，核对正常运行后的默认本地分配、cpuset 限制优先，以及任务策略改变只影响之后的分配。正文限定首次触发实际分配的场景，没有把 `malloc()` 调用者或只读缺页一概当作新私有页落点，表述成立。核查：[NUMA Memory Policy](https://docs.kernel.org/admin-guide/mm/numa_memory_policy.html)。
- **23.3，CPU 限制与内存迁移**：实际定位 cgroup v2 的 `cpuset.cpus.effective`、`cpuset.mems` 与 `cpuset.mems.effective`。正文“限制在某组 CPU 不等于搬走内存”指 CPU 限制，不是在说修改 `cpuset.mems` 永不迁移；后者文档确实规定可能触发迁移，正文未与其冲突。核查：[cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html)。
- **23.4，三类地址与 coherent DMA**：实际打开 DMA API Guide，核对 CPU 虚拟／物理地址与设备总线地址的区别，以及 IOMMU／桥接映射。进一步定位 coherent 映射仍可能需要屏障、streaming 映射需遵守同步协议的说明。正文没有把 coherent 解释为自动满足所有访问顺序，表述成立。核查：[Dynamic DMA mapping Guide](https://docs.kernel.org/core-api/dma-api-howto.html)。
- **23.4，IOMMU group 与拓扑**：实际打开 VFIO，核对设备、互连、桥接及多功能设备可能减弱单设备隔离粒度。正文没有声称启用 IOMMU 就能安全独立分配任意 PCI 功能，表述成立。核查：[VFIO](https://docs.kernel.org/driver-api/vfio.html)。
- **23.4–23.5，设备位置线索与客户机／宿主策略**：实际打开 PCI sysfs 中 `local_cpus` 定义，以及 QEMU Invocation 的客户机 `-numa` 与内存后端 `host-nodes`／`policy` 选项。正文把两张地图分开，没有声称客户机 NUMA 配置自动约束宿主布局，表述成立。核查：[PCI sysfs](https://docs.kernel.org/PCI/sysfs-pci.html)、[QEMU Invocation](https://www.qemu.org/docs/master/system/invocation.html)。

## 未覆盖与未实测

未执行软件安装、仓库签名链攻击测试、系统回滚、数据库迁移、NUMA 页迁移、绑核、DMA 驱动或 VFIO 设备直通，也没有运行性能基准。本轮重点为上述接口与边界的文献核对，不包含配图视觉校验、全书构建或逐条外链可用性的自动测试。Nix 以正文固定的 2.34 文档为准；内核及 QEMU 的滚动文档可能变化，实际操作仍需匹配目标版本。
