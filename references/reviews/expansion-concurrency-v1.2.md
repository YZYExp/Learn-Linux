# 第 21 章交叉审稿：并发与同步

审稿日期：2026-10-22。审稿者独立核对第 21 章当前正文与关键一手引用；未修改正文。范围包括 C++ 发布与数据竞争、GCC volatile、LKMM 边界、futex 等待／唤醒、POSIX 条件等待与伪共享。当前未见应阻止合并的事实错误；建议收紧两处表述，避免把有条件的接口保证读成无条件保证。

## 具体建议

| 等级 | 位置 | 问题与依据 | 建议 |
| --- | --- | --- | --- |
| 低：精确措辞 | 21.3，“正确协议中的状态变化若已发生，等待者不会还按旧判断开始睡眠” | FUTEX_WAIT 检查的是当前 futex word 是否仍等于预期值；不是记录任意历史变化。正文随后已有“状态复用”限制，整体方向正确，但前句单独摘读仍可能忽略值变化后又恢复的情况。[FUTEX_WAIT 描述](https://man7.org/linux/man-pages/man2/FUTEX_WAIT.2const.html) | 改为“若进入等待时该值已不等于预期值，调用就不会按旧判断开始睡眠”；保留状态复用、生命周期的现有限制。 |
| 低：前置条件与返回限定 | 21.3，条件变量段“返回时重新持有锁” | POSIX 明确要求调用前当前线程已持有传入互斥锁，且规定成功返回时持锁；错误情形另有规则。本章无操作代码，未构成错误示范，但加限定更稳妥。[POSIX 条件等待 DESCRIPTION](https://man7.org/linux/man-pages/man3/pthread_cond_wait.3p.html) | 改为“调用线程须先持有指定互斥锁；等待原子地释放锁并阻塞，成功返回时重新持有锁”；不必展开全部 robust mutex 错误码。 |

## 核查通过的边界

- 21.1 已将 C++ 数据竞争与业务竞态分开，未把未定义行为简化成“少加一次”。[C++ 工作草案 intro.races](https://eel.is/c++draft/intro.races)
- 21.2 已明确 release／acquire 的读值关系；relaxed 不承担普通数据发布所需的同步，seq_cst 不修复其他数据竞争。对“一次性发布”的生命周期限制表述合理。[atomics.order](https://eel.is/c++draft/atomics.order)
- 原子类型无锁实现并非普遍保证，文中保留查询及类型／平台差异；GCC 原子操作可能调用外部运行库的描述有依据。[C++ 原子类型操作](https://eel.is/c++draft/atomics.types.operations)、[GCC __atomic](https://gcc.gnu.org/onlinedocs/gcc/_005f_005fatomic-Builtins.html)
- volatile 没有被当成线程同步或普通对象发布的替代；LKMM 与用户态 C++ 规则已分开，也未把 READ_ONCE 当成完整同步。[GCC volatile](https://gcc.gnu.org/onlinedocs/gcc/Volatiles.html)、[LKMM Recipes](https://docs.kernel.org/dev-tools/lkmm/docs/recipes.html)
- 无竞争锁路径“可以”停留在用户态的措辞适当，没有将所有锁实现都说成相同路径；FUTEX_WAKE 的数量上限、选择不保证、唤醒不等于持锁及重新检查条件都准确。[futex(2)](https://man7.org/linux/man-pages/man2/futex.2.html)、[FUTEX_WAKE](https://man7.org/linux/man-pages/man2/FUTEX_WAKE.2const.html)
- 伪共享需要同缓存行共享与至少一方写入，不要求修改同一源代码变量；文中未把缓存行长度硬编码为所有架构常量，也未承诺盲目填充一定更快。[False Sharing](https://docs.kernel.org/kernel-hacking/false-sharing.html)

## 未覆盖与图示待核

未运行 C++ litmus test、ThreadSanitizer、futex 自制锁或 perf c2c；无对性能倍数或生产级实现正确性的认证。图 21-1 在本次事实审稿时尚未生成，不能据此声明已完成图文或移动端视觉审校。建议图中保留“被唤醒后重新竞争／检查”的回路，不画成 FUTEX_WAKE 直接授予锁；不要把有竞争路径画成每次加锁都必经内核。
