#include <stdint.h>
#include <avr/pgmspace.h>
#include <avr/interrupt.h>

#define MEM_POOL_SIZE 4096
static uint8_t __attribute__((section(".noinit"))) mem_pool[MEM_POOL_SIZE];
static size_t mem_ptr = 0;

void* qc_malloc(size_t size) {
    if (mem_ptr + size > MEM_POOL_SIZE) return NULL;
    void* ptr = &mem_pool[mem_ptr];
    mem_ptr += size;
    return ptr;
}

void qc_free(void* ptr) {
    // 无自动回收的静态分配
}

__attribute__((naked)) 
void _start() {
    asm volatile (
        "cli\n"
        "ldi r30, lo8(mem_pool)\n"
        "ldi r31, hi8(mem_pool)\n"
        "sts mem_ptr, r30\n"
        "sts mem_ptr+1, r31\n"
        "call main\n"
        "1: jmp 1b\n"
    );
}

// 精简版内存操作函数
void* memset(void* s, int c, size_t n) {
    uint8_t* p = (uint8_t*)s;
    while(n--) *p++ = c;
    return s;
}

void* memcpy(void* dest, const void* src, size_t n) {
    uint8_t* d = (uint8_t*)dest;
    const uint8_t* s = (const uint8_t*)src;
    while(n--) *d++ = *s++;
    return dest;
}
