"""Unit tests for the DiffElement class.

Copyright (c) 2020 Network To Code, LLC <info@networktocode.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from diffsync.diff import DiffElement


def test_diff_element_empty():
    """Test the basic functionality of the DiffElement class when initialized and empty."""
    element = DiffElement("interface", "eth0", {"device_name": "device1", "name": "eth0"})

    assert element.type == "interface"
    assert element.name == "eth0"
    assert element.keys == {"device_name": "device1", "name": "eth0"}
    assert element.source_name == "source"
    assert element.dest_name == "dest"
    assert element.source_attrs is None
    assert element.dest_attrs is None
    assert list(element.get_children()) == []
    assert not element.has_diffs()
    assert not element.has_diffs(include_children=True)
    assert not element.has_diffs(include_children=False)
    assert element.get_attrs_keys() == []

    element2 = DiffElement(
        "interface", "eth0", {"device_name": "device1", "name": "eth0"}, source_name="S1", dest_name="D1"
    )
    assert element2.source_name == "S1"
    assert element2.dest_name == "D1"


def test_diff_element_str_with_no_diffs():
    element = DiffElement("interface", "eth0", {"device_name": "device1", "name": "eth0"})
    assert element.str() == "interface: eth0 (no diffs)"


def test_diff_element_dict_with_no_diffs():
    element = DiffElement("interface", "eth0", {"device_name": "device1", "name": "eth0"})
    assert element.dict() == {}


def test_diff_element_attrs():
    """Test the basic functionality of the DiffElement class when setting and retrieving attrs."""
    element = DiffElement("interface", "eth0", {"device_name": "device1", "name": "eth0"})

    source_attrs = {"interface_type": "ethernet", "description": "my interface"}
    element.add_attrs(source=source_attrs)
    assert element.source_attrs == source_attrs

    assert element.has_diffs()
    assert element.has_diffs(include_children=True)
    assert element.has_diffs(include_children=False)
    assert element.get_attrs_keys() == source_attrs.keys()

    dest_attrs = {"description": "your interface"}
    element.add_attrs(dest=dest_attrs)
    assert element.source_attrs == source_attrs
    assert element.dest_attrs == dest_attrs

    assert element.has_diffs()
    assert element.has_diffs(include_children=True)
    assert element.has_diffs(include_children=False)
    assert element.get_attrs_keys() == ["description"]  # intersection of source_attrs.keys() and dest_attrs.keys()


def test_diff_element_str_with_diffs():
    element = DiffElement("interface", "eth0", {"device_name": "device1", "name": "eth0"})
    element.add_attrs(source={"interface_type": "ethernet", "description": "my interface"})
    assert element.str() == "interface: eth0 MISSING in dest"
    element.add_attrs(dest={"description": "your interface"})
    assert (
        element.str()
        == """\
interface: eth0
  description    source(my interface)    dest(your interface)\
"""
    )


def test_diff_element_dict_with_diffs():
    element = DiffElement("interface", "eth0", {"device_name": "device1", "name": "eth0"})
    element.add_attrs(source={"interface_type": "ethernet", "description": "my interface"})
    assert element.dict() == {"_src": {"description": "my interface", "interface_type": "ethernet"}}
    element.add_attrs(dest={"description": "your interface"})
    assert element.dict() == {"_dst": {"description": "your interface"}, "_src": {"description": "my interface"}}


def test_diff_element_children():
    """Test the basic functionality of the DiffElement class when storing and retrieving child elements."""
    child_element = DiffElement("interface", "eth0", {"device_name": "device1", "name": "eth0"})
    parent_element = DiffElement("device", "device1", {"name": "device1"})

    parent_element.add_child(child_element)
    assert list(parent_element.get_children()) == [child_element]
    assert not parent_element.has_diffs()
    assert not parent_element.has_diffs(include_children=True)
    assert not parent_element.has_diffs(include_children=False)

    source_attrs = {"interface_type": "ethernet", "description": "my interface"}
    dest_attrs = {"description": "your interface"}
    child_element.add_attrs(source=source_attrs, dest=dest_attrs)

    assert parent_element.has_diffs()
    assert parent_element.has_diffs(include_children=True)
    assert not parent_element.has_diffs(include_children=False)


def test_diff_element_str_with_child_diffs():
    child_element = DiffElement("interface", "eth0", {"device_name": "device1", "name": "eth0"})
    parent_element = DiffElement("device", "device1", {"name": "device1"})
    parent_element.add_child(child_element)
    source_attrs = {"interface_type": "ethernet", "description": "my interface"}
    dest_attrs = {"description": "your interface"}
    child_element.add_attrs(source=source_attrs, dest=dest_attrs)

    assert (
        parent_element.str()
        == """\
device: device1
  interface
    interface: eth0
      description    source(my interface)    dest(your interface)\
"""
    )


def test_diff_element_dict_with_child_diffs():
    child_element = DiffElement("interface", "eth0", {"device_name": "device1", "name": "eth0"})
    parent_element = DiffElement("device", "device1", {"name": "device1"})
    parent_element.add_child(child_element)
    source_attrs = {"interface_type": "ethernet", "description": "my interface"}
    dest_attrs = {"description": "your interface"}
    child_element.add_attrs(source=source_attrs, dest=dest_attrs)

    assert parent_element.dict() == {
        "interface": {"eth0": {"_dst": {"description": "your interface"}, "_src": {"description": "my interface"}}},
    }