import os


__all__ = ['get_db_path', 'get_models_dir', 'get_runs_dir',
           'get_model_data_dir', 'get_run_data_dir',
           'make_dir_writable', 'is_storage_exist', 'create_storage_directory']


def get_db_path(root):
    return os.path.join(root, 'db.sqlite3')


def get_models_dir(root):
    return os.path.join(root, 'models')


def get_runs_dir(root):
    return os.path.join(root, 'runs')


def get_model_data_dir(root, model):
    return os.path.join(get_models_dir(root), model.key['uid'])


def get_run_data_dir(root, run):
    runs_dir = get_runs_dir(root)
    return os.path.join(runs_dir, run.key['uid'])


def make_dir_writable(dir_path):
    os.makedirs(dir_path, exist_ok=True)
    return os.access(dir_path, os.W_OK)


def is_storage_exist(root_dir):
    return os.path.isdir(root_dir) \
        and os.path.isfile(get_db_path(root_dir)) \
        and os.path.isdir(get_models_dir(root_dir))


def create_storage_directory(root_dir):
    return make_dir_writable(get_models_dir(root_dir))
