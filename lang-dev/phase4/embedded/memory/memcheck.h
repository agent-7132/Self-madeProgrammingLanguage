#pragma once
#include <stddef.h>
#include <stdlib.h>

typedef struct {
    void* base;
    size_t size;
} MemoryBlock;

#define MEMCHECK_ALLOC(size) \
    do { \
        if (memory_watermark + (size) > ARENA_SIZE) { \
            abort(); \
        } \
    } while(0)

inline int check_memory_safety(MemoryBlock block) {
    return (block.base != NULL) && (block.size > 0);
}
