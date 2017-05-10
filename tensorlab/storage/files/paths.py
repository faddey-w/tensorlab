import os


__all__ = ['get_db_path', 'get_models_dir', 'get_model_path', 'get_config_path',
           'get_instances_dir', 'get_instance_path',
           'get_model_def_path', 'get_checkpoints_dir', 'get_runs_dir',
           'make_dir_writable', 'is_storage_exist', 'create_storage_directory']


def get_db_path(root):
    return os.path.join(root, 'db.sqlite3')


def get_config_path(root):
    return os.path.join(root, 'config.json')


def get_models_dir(root):
    return os.path.join(root, 'models')


def get_model_path(root, group, model):
    model_dir = '{}-{}'.format(model.name, model.uid)
    return os.path.join(get_models_dir(root), group.name, model_dir)


def get_instances_dir(model_dir):
    return os.path.join(model_dir, 'instances')


def get_instance_path(model_dir, instance_name):
    return os.path.join(get_instances_dir(model_dir), instance_name)


def get_model_def_path(model_dir):
    return os.path.join(model_dir, 'model.def')


def get_checkpoints_dir(instance_dir):
    return os.path.join(instance_dir, 'checkpoints')


def get_runs_dir(instance_dir):
    return os.path.join(instance_dir, 'runs')


def make_dir_writable(dir_path):
    os.makedirs(dir_path, exist_ok=True)
    return os.access(dir_path, os.W_OK)


def is_storage_exist(root_dir):
    return os.path.isdir(root_dir) \
        and os.path.isfile(get_db_path(root_dir)) \
        and os.path.isdir(get_models_dir(root_dir))


def create_storage_directory(root_dir):
    return make_dir_writable(get_models_dir(root_dir))
