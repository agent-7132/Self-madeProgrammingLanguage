const { performance } = require('perf_hooks');
const fs = require('fs/promises');

async function measureColdStart() {
  const wasmBuffer = await fs.readFile('compiler.wasm');
  const compileStart = performance.now();
  
  const { instance } = await WebAssembly.instantiate(wasmBuffer, {
    env: {
      memoryBase: 0,
      tableBase: 0,
      memory: new WebAssembly.Memory({ initial: 256 }),
      table: new WebAssembly.Table({ initial: 0, element: 'anyfunc' })
    }
  });
  
  const instantiateEnd = performance.now();
  instance.exports._initialize();
  const initEnd = performance.now();
  
  return {
    instantiateTime: instantiateEnd - compileStart,
    initTime: initEnd - instantiateEnd,
    totalTime: initEnd - compileStart
  };
}

module.exports = {
  run: async () => {
    const results = [];
    for (let i = 0; i < 100; i++) {
      const result = await measureColdStart();
      results.push(result);
    }
    return results;
  }
};
