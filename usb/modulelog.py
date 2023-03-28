import logging
from rich.logging import RichHandler
import rich
from rich.pretty import pprint as rich_pprint
from importlib import import_module

class ModuleLogging:
    def __init__(self, name) -> None:
        self.log = logging.getLogger(name)
        self.log.addHandler(logging.NullHandler())
        self.console = None
        self.handler = None
    def pprint(self, obj, **kwargs):
        if not self.log.isEnabledFor(logging.DEBUG): return
        rich_pprint(obj,**kwargs)
    def setLevel(self, level=logging.DEBUG, console=None):
        if self.console is None:
            if console is None:
                console = rich.get_console()
            self.console = console
        if self.handler is None:
            self.handler = self.log_handler()
            self.log.addHandler(self.handler)
        self.log.setLevel(level)
    def log_handler(self):
        return RichHandler(
            rich_tracebacks=True,
            console=self.console,
            show_level=False,
            show_time=False,
            show_path=False
        )
    def init(self):
        return self.log, self.pprint

def setLevel(modules, level:str='debug', console=rich.get_console()):
    levels = {
        'critical': logging.CRITICAL,
        'error': logging.ERROR,
        'warning': logging.WARNING,
        'info': logging.INFO,
        'debug': logging.DEBUG
    }
    for module_name in modules:
        import_module(module_name).module_log.setLevel(levels[level],console)