#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <wiringPi.h>
#include <signal.h>
#include <unistd.h>

typedef struct {
    uint8_t* base;
    size_t size;
} MemoryBlock;

static volatile sig_atomic_t cleanup_flag = 0;

void signal_handler(int sig) {
    cleanup_flag = 1;
}

MemoryBlock allocate_manual(size_t size) {
    MemoryBlock block;
    block.base = (uint8_t*)malloc(size);
    if (block.base == NULL) {
        fprintf(stderr, "内存分配失败\n");
        exit(EXIT_FAILURE);
    }
    block.size = size;
    return block;
}

void free_manual(MemoryBlock* block) {
    if (block->base != NULL) {
        free(block->base);
        block->base = NULL;
        block->size = 0;
    }
}

int check_memory_safety(MemoryBlock block) {
    return (block.base != NULL && block.size > 0);
}

void quantum_gate(int pin, float angle) {
    if (wiringPiSetup() == -1) {
        fprintf(stderr, "GPIO初始化失败\n");
        exit(EXIT_FAILURE);
    }
    
    if (angle < 0 || angle > 1.0f) {
        fprintf(stderr, "非法角度值: %f\n", angle);
        return;
    }
    
    pinMode(pin, OUTPUT);
    digitalWrite(pin, (angle > 0.5f) ? HIGH : LOW);
}

int main() {
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    
    MemoryBlock mem = allocate_manual(1024);
    if (!check_memory_safety(mem)) {
        fprintf(stderr, "内存初始化失败\n");
        return EXIT_FAILURE;
    }

    while (!cleanup_flag) {
        quantum_gate(1, 0.7f);
        usleep(100000);  // 100ms延迟
    }

    free_manual(&mem);
    printf("安全退出\n");
    return EXIT_SUCCESS;
}
