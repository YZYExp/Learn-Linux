# 第二轮独立交叉审稿：隔离、虚拟化与平台

审稿日期：2026-10-22。审稿基线为本次从当前工程包展开的第 1.0 版。本轮仅生成意见，未修改正文或图解。

## 审读范围与结论

已完整通读第 10、11、12、13、18、19 章，读取六幅对应 SVG 的文字、分层标签和图注，检查跨章概念关系。对关键事实重新读取 Linux 内核、man-pages、OCI、QEMU、AOSP、Apple 与直接研究项目资料，而非仅检查链接存在。

未发现需要推翻章节主线的重大机制错误。确证一项应补充的适用条件：`cpu.max` 不能被理解为所有调度类的统一 CPU 带宽上限。另有一项可选用词精化，不算独立事实错误。

## 确证问题

### VMP-01：`cpu.max` 的调度类别边界未写出

- **严重度：P2，适用范围精度问题。** 不影响普通服务使用公平调度的主要教学案例，但读者可能把限额保证外推到不适用的调度类。
- **位置：** 第 10 章“cgroup 管预算，不替你安排所有资源”首段及随后的预算耗尽情境。
- **原文短引：** “`cpu.max` 表示一个周期内可消耗的 CPU 时间预算”。
- **问题：** 该句没有限定调度类别，容易被读成“该组所有任务都统一受此预算约束”。当前内核文档将公平类任务、带相应回调的 BPF 调度任务以及其他任务分开，并对 `cpu.max` 明示其作用范围。实时与 deadline 策略不能照此推导。
- **原始来源：** [Control Group v2 — CPU Interface Files，cpu.max](https://docs.kernel.org/admin-guide/cgroup-v2.html#cpu-interface-files)。原文在 `cpu.max` 条目下说明该接口作用于公平类调度任务，以及实现 `cgroup_set_bandwidth` 回调的 BPF 调度器；同节将 `SCHED_FIFO`、`SCHED_RR`、`SCHED_DEADLINE` 列为另一类。资料于本轮实际读取。
- **建议最小修订：** 在原句后补：“这里以常规公平调度任务为例；实时、deadline 或扩展调度策略是否受相同带宽控制，必须另查对应调度机制，不能把 `cpu.max` 当成适用于所有任务的统一上限。” 若不展开扩展调度，保留上述一条范围提醒即可。
- **联动检查建议：** 其他章节若复用“组内预算耗尽”的推演，统一注明普通公平调度案例；不必增加实时调度的完整教程。图 10 只概括 cgroup 资源管理，不含具体所有调度类保证，无须改图。

## 可选精化，不计为确证错误

第 18 章写“Stable AIDL 为跨平台与厂商边界的接口提供稳定性要求”。这里的“跨平台”可能被误读为跨不同操作系统的兼容。可改为“Android 系统组件与厂商组件之间”等更具体的表述。[AOSP AIDL for HALs](https://source.android.com/docs/core/architecture/aidl/aidl-hals) 描述的是 `system.img` 与 `vendor.img` 等组件边界。当前上下文已经在谈 Android，因此这属于减少歧义，不应夸大为架构性错误。

## 已重点核实且可保留的表述

| 章节 | 重点核实项 | 结论与原始资料 |
| --- | --- | --- |
| 10 | namespace 类型与视图、user namespace 内外身份 | 与 [namespaces(7)](https://man7.org/linux/man-pages/man7/namespaces.7.html)、[user_namespaces(7)](https://man7.org/linux/man-pages/man7/user_namespaces.7.html) 的范围一致 |
| 10 | capabilities 每线程属性 | [capabilities(7)](https://man7.org/linux/man-pages/man7/capabilities.7.html) 直接支持；没有把 capability 说成唯一权限总开关 |
| 10 | seccomp 检查直接参数但不能任意解引用指针、并非完整沙箱 | [Seccomp BPF](https://docs.kernel.org/userspace-api/seccomp_filter.html) 支持；正文未将 syscall 过滤混成完整路径策略 |
| 10 | LSM 提供安全检查框架 | [Linux Security Module Usage](https://docs.kernel.org/admin-guide/LSM/index.html) 支持；正文未照搬该页可能过时的所有模块组合限制 |
| 11 | 镜像规范与运行时 bundle、Linux namespaces 配置分开 | [OCI image-spec](https://github.com/opencontainers/image-spec/blob/main/spec.md)、[bundle](https://github.com/opencontainers/runtime-spec/blob/main/bundle.md)、[Linux configuration](https://github.com/opencontainers/runtime-spec/blob/main/config-linux.md) 支持 |
| 11 | PID 1 的命名空间 init 职责与特殊信号规则 | [pid_namespaces(7)](https://man7.org/linux/man-pages/man7/pid_namespaces.7.html) 支持；无“应用一成为 PID 1 就自动正确回收子进程”的错误保证 |
| 11 | Docker rootless 与仅做 userns-remap 区分 | [Docker Rootless mode](https://docs.docker.com/engine/security/rootless/) 直接区分守护进程是否也非特权运行 |
| 12 | `/dev/kvm`、VM/vCPU fd、共享运行结构 | [KVM API](https://docs.kernel.org/virt/kvm/api.html) 支持，图注明确不是全部退出都回用户空间 |
| 12 | x86 二级地址转换与影子页表 | [x86 KVM MMU](https://docs.kernel.org/virt/kvm/x86/mmu.html) 支持；正文有架构限定，没有当作所有平台固定实现 |
| 12 | vhost-user 与内核 vhost 的处理位置有别 | [QEMU Vhost-user Protocol](https://www.qemu.org/docs/master/interop/vhost-user.html) 支持独立用户态后端和控制协议职责 |
| 12 | VFIO、IOMMU 与设备分组 | [VFIO](https://docs.kernel.org/driver-api/vfio.html) 支持；没有承诺任意设备都可安全单独分配 |
| 13 | user-mode 与 system emulation 范围不同 | [QEMU user space emulator](https://www.qemu.org/docs/master/user/main.html) 支持 syscall、信号、线程等转换职责；没有把指令翻译说成通用跨 OS 兼容 |
| 13 | TCG 翻译块与 CPU 状态条件 | [Translator Internals](https://www.qemu.org/docs/master/devel/tcg.html) 支持，不必为了科普展开全部 TB 失效路径 |
| 13 | 静态重编译仍需运行时与平台接口 | [N64ModernRuntime](https://github.com/N64Recomp/N64ModernRuntime) 的 ultramodern、回调与 renderer 分工直接支持；HLE 归类已标为方法解释 |
| 18 | ART 与操作系统进程不同层 | [Android runtime and Dalvik](https://source.android.com/docs/core/runtime) 支持 DEX 与托管运行时职责；正文避免了“安装时永远完成全部 AOT”绝对化 |
| 18 | Binderized HAL 与受约束的同进程例外 | [HAL overview](https://source.android.com/docs/core/architecture/hal) 明列两者；图注不把抽象框都当作进程 |
| 18 | KMI 有限定分支、配置与工具链范围 | [Maintain a stable KMI](https://source.android.com/docs/core/architecture/kernel/stable-kmi) 支持；正文“同一 LTS 与 Android 版本分支及构建条件”足以建立边界 |
| 19 | XNU 与 Linux 区分 | [Apple XNU](https://github.com/apple-oss-distributions/xnu) 明确说明 Darwin 与 Mach、FreeBSD、IOKit 等组成 |
| 19 | Horizon 微内核原则的证据身份 | [Atmosphère mesosphère](https://github.com/Atmosphere-NX/Atmosphere/blob/master/docs/components/mesosphere.md) 是直接重实现项目资料；正文已明确非任天堂原始源码、非全版本保证 |

## 审稿边界

本轮是完整文本审读与重点原文抽查，不是对每个引用页面逐段穷尽的形式化验证。SVG 在本轮检查的是语义标签、职责与图注，不宣称重新完成所有尺寸的视觉排版检查。没有执行特权容器、虚拟机、实时调度、Android 或 Switch 设备测试；也没有据此认证任何具体商业平台的兼容性。
