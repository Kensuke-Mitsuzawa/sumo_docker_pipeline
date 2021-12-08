import pathlib
from xml import etree
from pathlib import Path
from typing import Dict, Any, Tuple, List, Optional
from lxml import etree

import copy
import dataclasses


@dataclasses.dataclass
class TargetAttributeObject(object):
    xpath: str
    key_name: str
    element: str
    value_object: Optional[Any] = None

    def __str__(self):
        return f'key={self.key_name} value={self.value_object} with xpath={self.xpath}'


@dataclasses.dataclass
class SubConfigFile(object):
    name_config_file: str
    name_config_element: str
    path_config_file: str
    element_wildcard: str = '?'
    is_wildcard_element: bool = False

    def __post_init__(self):
        self.element_with_wildcard = self.find_wildcard_element_xpath()
        self.tree_original = etree.parse(self.path_config_file)
        self.tree_update = None
        if len(self.element_with_wildcard) > 0:
            self.is_wildcard_element = True

    def write_out_update_tree(self, path_destination: str):
        if self.tree_update is None:
            raise Exception(f'For {self.name_config_file}. tree_update is None. You have to update values.')
        # end if
        __ = self.find_wildcard_element_xpath(self.tree_update)
        if len(__) > 0:
            raise Exception(f'The target should be filled still. {__}')
        # end if
        self.tree_update.write(path_destination)

    def update_values(self, values: Dict[str, Any]):
        """update values and write the Tree out into XML file.

        Example of values:
        >>> {'/routes/flows/vType[1]': {'maxSpeed': 15, 'minGap': 1.0, 'accel': 10, 'decel': 5}}

        :param values: {'xPath': {element-key: element-value-object}. The object can be multiple-layer dict objects.
        :param path_destination: a path to write the tree out.
        :return: None
        """
        config_objects = copy.deepcopy(self.element_with_wildcard)
        for elem_obj in config_objects:
            xpath_required = elem_obj.xpath
            assert xpath_required in values, f'{xpath_required} must be in the given values object. ' \
                                             f'The existing keys are {values.keys()}'
            update_object = values[xpath_required]
            key_name_required = elem_obj.key_name
            assert key_name_required in values[xpath_required], \
                f'{key_name_required} must be in the given values object. Actual object={values[xpath_required]}'
            value_update = update_object[key_name_required]
            elem_obj.value_object = value_update
        # end for
        self.replace_wildcard_element(target_values=config_objects)

    def replace_wildcard_element(self,
                                 target_values: List[TargetAttributeObject]):
        """fulfill the position with wildcard and write a tree out to a file"""
        tree = copy.deepcopy(self.tree_original)
        for att_object in target_values:
            elem_obj = tree.xpath(att_object.xpath)
            assert len(elem_obj) == 1
            elem_attribute_object = elem_obj[0].attrib
            elem_attribute_object[att_object.key_name] = str(att_object.value_object)
        # end for
        # double-check if a wildcard object does not exist
        __ = self.find_wildcard_element_xpath(tree)
        if len(__) > 0:
            raise Exception(f'The target should be filled still. {__}')
        # end if
        # tree.write(path_destination)
        self.tree_update = tree

    def find_wildcard_element_xpath(self, tree = None) -> List[TargetAttributeObject]:
        """find a XPath and a key that an attribute == ?"""
        target_attributes = []
        if tree is None:
            tree = etree.parse(self.path_config_file)
        # end if

        for elem in tree.iter():
            if len(elem.getchildren()) > 0:
                continue
            # end if
            if '?' in elem.attrib.values():
                __xpath = tree.getpath(elem)
                __element_txt: str = etree.tostring(elem).decode('utf-8').strip()
                __keys_target = [__k for __k, __v in elem.attrib.items() if __v == '?']
                for k_name in __keys_target:
                    target_attributes.append(TargetAttributeObject(__xpath, k_name, __element_txt))
            # end if
        # end for
        return target_attributes


class Template2SuMoConfig(object):
    def __init__(self,
                 path_config_file: Path,
                 path_destination_dir: Path):
        assert Path(path_config_file).exists()
        if not Path(path_destination_dir).exists():
            path_destination_dir.mkdir()
        # end if

        self.path_config_file = str(pathlib.Path(path_config_file).absolute())
        self.path_config_dir = str(pathlib.Path(path_config_file).parent)
        self.name_sumo_cfg = Path(path_config_file).name
        self.path_destination_dir = path_destination_dir
        # set root and sub config files
        __sub_config_files = self.__extract_input_options(str(path_config_file))
        __sub_config_files.append(self.__set_root_cfg_config_object(self.path_config_file))
        self.config_files = __sub_config_files

    def __set_root_cfg_config_object(self, path_config_file: str) -> SubConfigFile:
        root_cfg_obj = SubConfigFile(Path(path_config_file).name, self.name_sumo_cfg, self.path_config_file)
        with open(self.path_config_file, 'r') as f:
            root_cfg_obj.tree_update = etree.parse(f)
        # end with
        return root_cfg_obj

    @staticmethod
    def __update_output_prefix(tree: etree.ElementTree) -> etree.ElementTree:
        """update 'output-prefix' element in the xml."""
        root = tree.getroot()
        output_element = root.find('output')
        if output_element is None:
            output_element = etree.Element('output')
            root.append(output_element)
        # end if
        output_prefix_element = output_element.find('output-prefix')
        if output_prefix_element is None:
            etree.SubElement(_parent=output_element, _tag='output-prefix', attrib={'value': 'output/'})
            output_element.insert(1, output_element[-1])
        else:
            output_prefix_element.attrib['value'] = 'output/'
        # end if
        return tree

    def __extract_input_options(self, config_file_name: str) -> List[SubConfigFile]:
        """extract path-to-config which is written in sumo.cfg file.

        :param config_file_name:
        :return: (option-name, path-config-file)
        """
        cfg_files = []

        tree = etree.parse(config_file_name)
        root = tree.getroot()
        for t in root.find('input'):
            element_name = t.tag
            value_name: Dict[str, Any] = t.attrib
            if isinstance(value_name['value'], bool):
                # remove boolean options
                continue
            if value_name['value'] in ('true', 'false'):
                continue
            # end if
            try:
                # remove int value option
                float(value_name['value'])
                continue
            except ValueError:
                path_cfg_file = value_name['value']
                if '..' in path_cfg_file:
                    raise Exception(f'config file must be in the same directory level or below level. {path_cfg_file}')
                # end if
                __sub_cfg_file: str = str(pathlib.Path(self.path_config_dir).joinpath(path_cfg_file))
                cfg_files.append(SubConfigFile(Path(__sub_cfg_file).name, element_name, __sub_cfg_file))
            # end try
        # end for
        return cfg_files

    def update_configs(self, update_values: Dict[str, Dict[str, Any]]) -> None:
        """Update `SubConfigFile` with the given values.

        Args:
            update_values: {"sub config file name": {"xml key": {values}}}
        Returns: None
        """
        d_sub_configs = self.get_config_objects()
        for file_name in update_values.keys():
            assert file_name in d_sub_configs, f'{file_name} does not exist in {self.path_config_dir}'
            d_sub_configs[file_name].update_values(update_values[file_name])

    def generate_updated_config_file(self,
                                     updated_config_object: Optional[List[SubConfigFile]] = None) -> None:
        """write out config files into a new directory.

        Args:
            updated_config_object:
        Returns:

        """
        # check the destination directory
        if not pathlib.Path(self.path_destination_dir).exists():
            pathlib.Path(self.path_destination_dir).mkdir()
        if not pathlib.Path(self.path_destination_dir).joinpath('output').exists():
            pathlib.Path(self.path_destination_dir).joinpath('output').mkdir()

        if updated_config_object is None:
            updated_config_object = self.config_files
        # end if

        for config_obj in updated_config_object:
            if self.name_sumo_cfg == config_obj.name_config_file:
                # update the path to output where SUMO saves the result.
                config_obj.tree_update = self.__update_output_prefix(config_obj.tree_update)
            # end if

            new_destination_path: str = str(Path(self.path_destination_dir).
                                            joinpath(f'{config_obj.name_config_file}'))
            # end if
            if config_obj.tree_update is None:
                config_obj.tree_update = config_obj.tree_original
            # end if
            config_obj.write_out_update_tree(new_destination_path)
        # end for

    def get_config_file_name_list(self) -> List[SubConfigFile]:
        """get list of config files"""
        return self.config_files

    def get_config_objects(self, is_only_wildcard: bool = False) -> Dict[str, SubConfigFile]:
        """Return `SubConfigFile` objects.

        Args:
            is_only_wildcard: returns `SubConfigFile` that has wildcards in the configuration.

        Returns: {config_file_name: `SubConfigFile`}
        """
        if is_only_wildcard:
            return {c.name_config_file: c for c in self.config_files if c.is_wildcard_element is True}
        else:
            return {c.name_config_file: c for c in self.config_files}