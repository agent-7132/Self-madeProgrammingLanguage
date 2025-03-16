#pragma once
#include <stddef.h>

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
    return (block.base != NULL) && 
           ((uintptr_t)block.base >= (uintptr_t)memory_arena) &&
           ((uintptr_t)block.base + block.size <= (uintptr_t)memory_arena + ARENA_SIZE);
}
