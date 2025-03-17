#pragma once
#include <stdalign.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdlib.h>

#define ARENA_SIZE (256 * 1024)
#define MEM_ALIGNMENT 64

static alignas(MEM_ALIGNMENT) uint8_t memory_arena[ARENA_SIZE];
static atomic_size_t memory_watermark = ATOMIC_VAR_INIT(0);

inline void* malloc_embedded(size_t size) {
    size = (size + MEM_ALIGNMENT - 1) & ~(MEM_ALIGNMENT - 1);
    size_t current = atomic_load(&memory_watermark);
    size_t new_watermark;

    do {
        new_watermark = current + size;
        if (new_watermark > ARENA_SIZE) return NULL;
    } while (!atomic_compare_exchange_strong(&memory_watermark, &current, new_watermark));

    return &memory_arena[current];
}

#ifdef DEBUG
#define MEMCHECK(ptr) do { \
    if ((uintptr_t)(ptr) % MEM_ALIGNMENT != 0) { \
        fprintf(stderr, "内存未对齐: %p\n", ptr); \
        abort(); \
    } \
    if ((uintptr_t)(ptr) < (uintptr_t)memory_arena || \
        (uintptr_t)(ptr) >= (uintptr_t)memory_arena + ARENA_SIZE) { \
        fprintf(stderr, "内存越界: %p\n", ptr); \
        abort(); \
    } \
} while (0)
#else
#define MEMCHECK(ptr)
#endif
