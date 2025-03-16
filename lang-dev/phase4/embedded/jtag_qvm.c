#include <stdint.h>
#include "memory.h"
#include "memory/memcheck.h"  // 新增安全检查

#define QVM_DEBUG_PORT 0x10000000
volatile uint32_t* debug_port = (uint32_t*)QVM_DEBUG_PORT;

void quantum_state_dump(uint32_t qubit_mask) {
  MEMCHECK_ALLOC(8);  // 内存安全检查
  uint64_t* state_ptr = (uint64_t*)malloc_embedded(8);
  assert(check_memory_safety((MemoryBlock){state_ptr,8}));
  
  *debug_port = 0x1;
  asm volatile("fence");
  while ((*debug_port & 0x80000000) == 0);
  uint32_t state_hi = *(debug_port + 1);
  uint32_t state_lo = *(debug_port + 2);
  *state_ptr = ((uint64_t)state_hi << 32) | state_lo;
}

// 保持原有单量子探针实现不变
#pragma GCC push_options
#pragma GCC optimize("O0")
void single_qubit_probe(uint8_t qubit_id) {
  *debug_port = 0x2 | (qubit_id << 8);
  asm volatile("fence.i");
  for (volatile int i = 0; i < 100; ++i);
}
#pragma GCC pop_options
