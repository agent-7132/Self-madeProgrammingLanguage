export class QuantumWASM {
  constructor(module) {
    this.memory = new WebAssembly.Memory({ initial: 256 });
    this.instance = new WebAssembly.Instance(module, {
      env: { 
        quantum_malloc: (size) => this._malloc(size),
        memory: this.memory 
      }
    });
  }

  _malloc(size) {
    const ptr = this.memory.buffer.byteLength;
    this.memory.grow(Math.ceil(size / 65536));
    return ptr;
  }
}

// 新增冷启动优化代码
export const initWASMPool = () => {
  const preAllocated = new ArrayBuffer(1024 * 1024);
  WebAssembly.Memory.prototype.grow.call(this.memory, preAllocated);
  console.log('Pre-allocated 1MB WASM memory pool');
};
