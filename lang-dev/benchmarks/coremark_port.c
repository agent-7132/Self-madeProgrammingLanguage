#include <stdint.h>
#include <coremark.h>

#if defined(__riscv)
#include <platform_riscv.h>
#elif defined(__wasm__)
#include <emscripten.h>
#endif

void portable_init() {
#if defined(__riscv)
    init_riscv_counter();
#elif defined(__wasm__)
    EM_ASM({ startWasmTimer(); });
#endif
}

int main() {
    portable_init();
    uint16_t iterations = 1000;
    
    struct results_t res;
    iterate(&res, iterations);
    
    print_result(res);
    return 0;
}
