#include <stdint.h>
#include "memory.h"

#define QVM_DEBUG_PORT 0x10000000

volatile uint32_t* debug_port = (uint32_t*)QVM_DEBUG_PORT;

void quantum_state_dump(uint32_t qubit_mask) {
  // JTAG调试接口交互
  *debug_port = 0x1;  // 触发状态捕获信号
  asm volatile("fence");  // 内存屏障
  
  while ((*debug_port & 0x80000000) == 0);  // 等待就绪信号
  uint32_t state_hi = *(debug_port + 1);
  uint32_t state_lo = *(debug_port + 2);
  
  // 将量子态写入安全内存区域
  uint64_t* state_ptr = (uint64_t*)malloc_embedded(8);
  *state_ptr = ((uint64_t)state_hi << 32) | state_lo;
}

#pragma GCC push_options
#pragma GCC optimize("O0")  // 禁用优化保证调试时序
void single_qubit_probe(uint8_t qubit_id) {
  // 发送单量子位探针脉冲
  *debug_port = 0x2 | (qubit_id << 8);
  asm volatile("fence.i");  // 指令同步屏障
  for (volatile int i = 0; i < 100; ++i);  // 等待脉冲完成
}
#pragma GCC pop_options
