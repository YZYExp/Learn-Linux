# 四个贯通案例的独立交叉审稿

核查日期：2026-10-22。审稿对象为 `cases/01-container.md` 至 `cases/04-slow-service.md` 的当前正文，以及四幅 `case-*.svg` 的 XML 与文字标签。未修改作者正文，未执行容器部署、数据库事务、虚拟机或性能实验。图文件已存在且可解析；本次没有完成图片渲染后的视觉审查，不能据此声称字号、连线与手机显示全部合格。

## 结论与需要处理的项

未发现把 OCI 镜像强制等同于 OverlayFS、把每次 VM exit 等同于返回 QEMU，或把 PSI 当作根因证明等主线错误。持久性案例有一处建议补足的配置前提，处理后可按当前教学范围合入。

### C1：明确保留完整页写保护（建议在合入前补足）

位置：案例二首段的教学条件，以及末段只读 `SHOW` 查询。

首段限定普通持久表、`fsync=on`、`synchronous_commit=on`，后文据此解释崩溃恢复。PostgreSQL 官方 `full_page_writes` 文档说明：页写入在系统故障中部分完成时，普通行级 WAL 变化可能不足以恢复该页；关闭完整页写会带来不可恢复或静默损坏风险，默认值为 `on`。

建议在教学前提增加“沿用默认 `full_page_writes=on`”，末段增加 `SHOW full_page_writes;`。无需扩写全部页撕裂实现，只需避免让读者以为前两个开关是全部持久性配置。若讨论替代页原子性保障，应另列目标文件系统／存储条件，而不能无条件省略。

证据：[PostgreSQL WAL 配置：full_page_writes](https://www.postgresql.org/docs/current/runtime-config-wal.html)、[PostgreSQL Reliability](https://www.postgresql.org/docs/current/wal-reliability.html)。核查时 current 页面显示 PostgreSQL 18；这是文档读取，不是目标环境测试。

## 已核对且在当前范围内成立

| 对象 | 核对结果 | 原始资料 |
| --- | --- | --- |
| 案例一：镜像、创建与启动 | 首段已明确 OverlayFS 是教学设定。图中另说明镜像层不强制 OverlayFS；OCI image layer 表达文件系统变化，runtime 的 created/running 状态不能代替应用就绪。 | [OCI image layer](https://github.com/opencontainers/image-spec/blob/main/layer.md)、[OCI runtime lifecycle](https://github.com/opencontainers/runtime-spec/blob/main/runtime.md) |
| 案例二：WAL 与提交 | 普通同步提交等待本地 WAL flush、数据页不必每次提交全部同步、多个并发事务可共享一次同步，与官方说明一致。正文已排除复制全部应用和任意硬件的无条件保证。 | [WAL introduction](https://www.postgresql.org/docs/current/wal-intro.html)、[WAL 配置](https://www.postgresql.org/docs/current/runtime-config-wal.html) |
| 案例二：检查点 | 检查点与逐次提交的等待边界已经区分。检查点完成节奏、写回和恢复范围的描述有配置文档支持，未把假设性能问题写成实测。 | [Checkpoints 参数](https://www.postgresql.org/docs/current/runtime-config-wal.html) |
| 案例三：执行与退出 | KVM fd/ioctl、KVM_RUN 和用户态机器组织的职责区分成立；正文主动区分硬件退出、内核处理和返回用户态。 | [KVM API](https://docs.kernel.org/virt/kvm/api.html)、[QEMU introduction](https://www.qemu.org/docs/master/system/introduction.html) |
| 案例三：virtio 与后端 | virtio 请求／完成队列不等于宿主文件路径，QEMU 设备模拟可卸载到其他进程；图中将后端视为职责而非唯一进程，未强制每次请求经过主线程。 | [virtio 1.2](https://docs.oasis-open.org/virtio/virtio/v1.2/virtio-v1.2.html)、[QEMU introduction](https://www.qemu.org/docs/master/system/introduction.html) |
| 案例四：CPU 与 cgroup | 正文要求结合控制器和上层层级，没有声称一个容器的叶级计数足以排除全部节流。应继续保留这一限定：当前文档明确部分带宽计数不包含祖先限制导致的节流。 | [cgroup v2：CPU Interface Files](https://docs.kernel.org/admin-guide/cgroup-v2.html) |
| 案例四：PSI | 正文没有把 some/full 混为同一口径，也明确系统级 CPU full 不能按普通压力比例理解；官方文档说明该值系统级未定义并为兼容返回零。 | [PSI 文档](https://docs.kernel.org/accounting/psi.html) |
| 案例四：数据库观察 | pg_stat_activity 用于当前活动与等待事件，正文区分动态信息和累计统计口径；相关性与因果性也已分开。 | [PostgreSQL monitoring statistics](https://www.postgresql.org/docs/current/monitoring-stats.html) |

## 未覆盖范围

本审稿没有逐项验证每一种运行时的挂载实现、Docker rootless 网络、所有 virtio 设备协商、QEMU 缓存模式、实际硬件 flush 履约或生产数据库参数。也没有对所有外链可达性作持久在线保证。上述事项不能从“本次未发现主线错误”推导为已经测试通过。
