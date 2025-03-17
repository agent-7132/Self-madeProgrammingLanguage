"""
Quantum Compiler CLI Package Initialization
"""

__version__ = "2.3.0"
__all__ = ['main', 'commands', 'compile', 'verify', 'debug']

from .main import cli
from .commands import (
    compile_cmd,
    verify_cmd,
    debug_cmd
)

def init_cli():
    """Initialize CLI components"""
    # Register all commands
    from .main import cli
    cli.add_command(compile_cmd)
    cli.add_command(verify_cmd)
    cli.add_command(debug_cmd)
    
    # Configure logging
    import logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

# Auto-initialize when imported
init_cli()
