from tensorlab.storage import TensorLabStorage


def init(args):
    storage = TensorLabStorage(args.root).Create()
    print('Created empty TensorLab at {}'.format(storage.root_dir))


def show(args):
    storage = TensorLabStorage(args.root).Open()
    print('Found TensorLab at {}'.format(storage.root_dir))


COMMANDS = {
    'init': init,
    'show': show,
}
