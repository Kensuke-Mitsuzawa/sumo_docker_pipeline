from sumo_docker_pipeline.config_generation_module import Template2SuMoConfig, SubConfigFile
from pathlib import Path


def test_generate_config(resource_path_root: Path):
    path_source_cfg = resource_path_root.joinpath('config_template').joinpath('grid.sumo.cfg').absolute()
    path_destination_dir = resource_path_root.joinpath('config_template/generated').absolute()
    if not path_destination_dir.exists():
        path_destination_dir.mkdir()
    # end if
    config_generator = Template2SuMoConfig(path_config_file=path_source_cfg,
                                           path_destination_dir=path_destination_dir)
    assert len(config_generator.config_files) == 4
    values_target = {
        '/routes/flows/vType[1]': {
            'maxSpeed': 15,
            'minGap': 1.0,
            'accel': 10,
            'decel': 5
        },
        '/routes/flows/vType[2]': {
            'maxSpeed': 10,
            'minGap': 0.5,
            'accel': 5,
            'decel': 5
        }
    }
    d_sub_configs = config_generator.get_config_objects()
    for file_name in d_sub_configs:
        d_sub_configs[file_name].update_values(values_target)
    # end for
    config_generator.generate_updated_config_file()
    assert path_destination_dir.exists()
    assert len(list(path_destination_dir.glob('*xml'))) == 3
    import shutil
    shutil.rmtree(path_destination_dir)


def test_config_object(resource_path_root: Path):
    path_config: str = str(resource_path_root.joinpath('config_template/grid.flows.xml'))
    sub_cfg_object = SubConfigFile('grid.flows.xml', 'flow', path_config)
    seq_elem_obj = sub_cfg_object.element_with_wildcard
    values_target = {
        'passenger': {
            'maxSpeed': 15,
            'minGap': 1.0,
            'accel': 10,
            'decel': 5
        },
        'pickup': {
            'maxSpeed': 10,
            'minGap': 0.5,
            'accel': 5,
            'decel': 5
        }
    }
    for v_type, v_spec in values_target.items():
        for key_spec, value_spec in v_spec.items():
            for elem_obj in seq_elem_obj:
                if v_type in elem_obj.element and key_spec == elem_obj.key_name:
                    elem_obj.value_object = value_spec
                # end if
            # end for
        # end for
    # end for
    sub_cfg_object.replace_wildcard_element(seq_elem_obj)


if __name__ == '__main__':
    test_generate_config(Path('./resources'))
    test_config_object(Path('./resources'))
