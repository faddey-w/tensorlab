import os


TENSORLAB_ROOT = None


def infer_tensorlab_root():
    root = os.environ.get('TENSORLAB')
    if not root:
        candidate = os.getcwd()
        while True:
            path = get_default_tensorlab_root(candidate)
            if os.path.isdir(path):
                root = path
                break
            next_candidate = os.path.dirname(candidate)
            if next_candidate == candidate:
                break
            else:
                candidate = next_candidate
    return root or None


def set_tensorlab_root(directory):
    global TENSORLAB_ROOT
    TENSORLAB_ROOT = directory


def get_tensorlab_root():
    if TENSORLAB_ROOT is None:
        raise Exception("TensorLab root is not defined")
    return TENSORLAB_ROOT


def get_default_tensorlab_root(directory=None):
    if directory is None:
        directory = os.getcwd()
    return os.path.join(directory, '.tensorlab')
