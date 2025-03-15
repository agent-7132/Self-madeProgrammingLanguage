#ifndef AMX_INTRIN_H
#define AMX_INTRIN_H

#include <immintrin.h>

typedef struct {
  uint8_t palette_id;
  uint8_t reserved[15];
} __tilecfg;

void _tile_loadconfig(const void* config) {
  asm volatile("ldtilecfg %0" :: "m"(*(const __tilecfg*)config));
}

void _tile_storeconfig(void* config) {
  asm volatile("sttilecfg %0" : "=m"(*(__tilecfg*)config));
}

void _tile_zero(int tile) {
  asm volatile("tilezero %%tmm%d" :: "i"(tile));
}

void _tile_loadd(int tile, const void* base, long stride) {
  asm volatile("tileloadd (%0,%1,1), %%tmm%d" :: "r"(base), "r"(stride), "i"(tile));
}

void _tile_stored(int tile, void* base, long stride) {
  asm volatile("tilestored %%tmm%d, (%0,%1,1)" :: "r"(base), "r"(stride), "i"(tile));
}

#endif // AMX_INTRIN_H
