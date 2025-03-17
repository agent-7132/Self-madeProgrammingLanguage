#pragma once
#include <stdint.h>
#include <stddef.h>
#include <string.h>

#define NO_GC
#define ARENA_SIZE (256 * 1024)

static uint8_t memory_arena[ARENA_SIZE];
static size_t memory_watermark = 0;

inline void* malloc_embedded(size_t size) {
    size_t aligned_size = (size + 7) & ~7;
    if (memory_watermark + aligned_size > ARENA_SIZE) {
        return NULL;
    }
    memset(&memory_arena[memory_watermark], 0, aligned_size);
    void* ptr = &memory_arena[memory_watermark];
    memory_watermark += aligned_size;
    return ptr;
}

inline void free_embedded(void* ptr) {}

#ifdef EMBEDDED
#define malloc(size) malloc_embedded(size)
#define free(ptr) ((void)0)
#endif
