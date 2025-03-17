import click
from .commands import compile, verify, debug
import json
import sys

def load_config(config_path):
    """加载配置文件"""
    try:
        with open(config_path) as f:
            return json.load(f)
    except Exception as e:
        print(f"加载配置文件失败: {str(e)}")
        sys.exit(1)

@click.group()
@click.option('--config', default='/opt/compiler/config/quantum.cfg', 
             help='配置文件路径')
@click.pass_context
def cli(ctx, config):
    """量子混合编译器命令行工具"""
    ctx.ensure_object(dict)
    ctx.obj['config'] = load_config(config)

@cli.command()
@click.argument('input_file')
@click.option('--target', '-t', 
             type=click.Choice(['qasm', 'qobj', 'llvm', 'cuda']),
             default='qasm', help='目标输出格式')
@click.pass_context
def compile_cmd(ctx, input_file, target):
    """编译量子程序"""
    config = ctx.obj['config']
    compile.run_compilation(input_file, target, config)

@cli.command()
@click.argument('contract_file')
@click.option('--formal', is_flag=True, help='启用形式化验证')
@click.pass_context
def verify_cmd(ctx, contract_file, formal):
    """验证智能合约安全性"""
    config = ctx.obj['config']
    verify.verify_contract(contract_file, formal, config)

@cli.command()
@click.argument('circuit_file')
@click.option('--hardware', default='simulator',
             help='选择调试硬件(simulator/quantum-processor)')
@click.pass_context
def debug_cmd(ctx, circuit_file, hardware):
    """量子电路调试器"""
    config = ctx.obj['config']
    debug.start_debug_session(circuit_file, hardware, config)

def healthcheck():
    """Docker健康检查接口"""
    try:
        from ..core import quantum_ir
        return 0
    except Exception as e:
        print(f"健康检查失败: {str(e)}")
        return 1

if __name__ == '__main__':
    cli(obj={})
