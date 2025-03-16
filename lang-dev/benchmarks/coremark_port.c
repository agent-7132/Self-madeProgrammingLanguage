#include <stdint.h>
#include <coremark.h>
#include <riscv_interrupt.h>  // 新增中断支持

// 新增抢占式调度实现
__attribute__((interrupt))
void scheduler_interrupt() {
    asm volatile(
        "csrrw sp, mscratch, sp\n"
        "j save_context\n"
    );
}

void portable_init() {
    riscv_enable_interrupt(TIMER_INTERRUPT);
    set_timer(1000);  // 每1ms触发一次抢占
}

#if defined(__riscv)
#include <platform_riscv.h>
#elif defined(__wasm__)
// 保持原有wasm支持
#endif

// 保持原有CoreMark实现不变
MAIN main() {
    portable_init();
    uint16_t iterations=0;
    core_init();
    while(iterations < 1000) {
        core_exec();
        iterations++;
    }
    core_report();
    return 0;
}
