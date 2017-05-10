from tensorlab.storage import TensorLabStorage
from . import _tools


def setup(commands):
    commands.add_parser('init')
    commands.add_parser('show')
    commands.add_parser('destroy')

    run_parser = commands.add_parser('run')
    run_parser.add_argument('instance_spec',
                            type=_tools.spec('{group}/{model}[/{instance}]'))
    run_parser.add_argument('--attr', type=_tools.attr_type, nargs='*')

    setconfig_parser = commands.add_parser('set')
    setconfig_parser.add_argument('key')
    setconfig_parser.add_argument('value')

    return {
        'init': init,
        'show': show,
        'set': set_config,
        'destroy': destroy,
        'run': run,
    }


def init(args):
    storage = TensorLabStorage(args.root).Create()
    print('Created empty TensorLab at {}'.format(storage.root_dir))


def show(args):
    storage = TensorLabStorage(args.root).Open()
    print('Found TensorLab at {}'.format(storage.root_dir))


def destroy(args):
    import shutil
    shutil.rmtree(args.root)


def set_config(args):
    raise NotImplementedError


def run(args):
    raise NotImplementedError
