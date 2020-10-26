"""Unit tests for the Diff class.

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

import pytest

from diffsync.diff import Diff, DiffElement
from diffsync.exceptions import ObjectAlreadyExists


def test_diff_empty():
    """Test the basic functionality of the Diff class when initialized and empty."""
    diff = Diff()

    assert diff.children == {}
    assert list(diff.groups()) == []
    assert not diff.has_diffs()
    assert list(diff.get_children()) == []


def test_diff_str_with_no_diffs():
    diff = Diff()

    assert diff.str() == "(no diffs)"


def test_diff_dict_with_no_diffs():
    diff = Diff()

    assert diff.dict() == {}


def test_diff_children():
    """Test the basic functionality of the Diff class when adding child elements."""
    diff = Diff()
    device_element = DiffElement("device", "device1", {"name": "device1"})
    intf_element = DiffElement("interface", "eth0", {"device_name": "device1", "name": "eth0"})

    diff.add(device_element)
    assert "device" in diff.children
    assert diff.children["device"] == {"device1": device_element}
    assert list(diff.groups()) == ["device"]
    assert not diff.has_diffs()
    assert list(diff.get_children()) == [device_element]
    with pytest.raises(ObjectAlreadyExists):
        diff.add(device_element)

    diff.add(intf_element)
    assert "interface" in diff.children
    assert diff.children["interface"] == {"eth0": intf_element}
    assert list(diff.groups()) == ["device", "interface"]
    assert not diff.has_diffs()
    assert list(diff.get_children()) == [device_element, intf_element]
    with pytest.raises(ObjectAlreadyExists):
        diff.add(intf_element)

    source_attrs = {"interface_type": "ethernet", "description": "my interface"}
    dest_attrs = {"description": "your interface"}
    intf_element.add_attrs(source=source_attrs, dest=dest_attrs)

    assert diff.has_diffs()


def test_diff_str_with_diffs():
    diff = Diff()
    device_element = DiffElement("device", "device1", {"name": "device1"})
    diff.add(device_element)
    intf_element = DiffElement("interface", "eth0", {"device_name": "device1", "name": "eth0"})
    source_attrs = {"interface_type": "ethernet", "description": "my interface"}
    dest_attrs = {"description": "your interface"}
    intf_element.add_attrs(source=source_attrs, dest=dest_attrs)
    diff.add(intf_element)

    # Since device_element has no diffs, we don't have any "device" entry in the diff string:
    assert (
        diff.str()
        == """\
interface
  interface: eth0
    description    source(my interface)    dest(your interface)\
"""
    )


def test_diff_dict_with_diffs():
    diff = Diff()
    device_element = DiffElement("device", "device1", {"name": "device1"})
    diff.add(device_element)
    intf_element = DiffElement("interface", "eth0", {"device_name": "device1", "name": "eth0"})
    source_attrs = {"interface_type": "ethernet", "description": "my interface"}
    dest_attrs = {"description": "your interface"}
    intf_element.add_attrs(source=source_attrs, dest=dest_attrs)
    diff.add(intf_element)

    assert diff.dict() == {
        "interface": {"eth0": {"_dst": {"description": "your interface"}, "_src": {"description": "my interface"}}},
    }


def test_order_children_default(backend_a, backend_b):
    """Test that order_children_default is properly called when calling get_children."""

    class MyDiff(Diff):
        """custom diff class to test order_children_default."""

        @classmethod
        def order_children_default(cls, children):
            """Return the children ordered in alphabetical order."""
            keys = sorted(children.keys(), reverse=False)
            for key in keys:
                yield children[key]

    # Validating default order method
    diff_a_b = backend_a.diff_from(backend_b, diff_class=MyDiff)
    children = diff_a_b.get_children()
    children_names = [child.name for child in children]
    assert children_names == ["atl", "nyc", "rdu", "sfo"]


def test_order_children_custom(backend_a, backend_b):
    """Test that a custom order_children method is properly called when calling get_children."""

    class MyDiff(Diff):
        """custom diff class to test order_children_site."""

        @classmethod
        def order_children_site(cls, children):
            """Return the site children ordered in reverse-alphabetical order."""
            keys = sorted(children.keys(), reverse=True)
            for key in keys:
                yield children[key]

    diff_a_b = backend_a.diff_from(backend_b, diff_class=MyDiff)
    children = diff_a_b.get_children()
    children_names = [child.name for child in children]
    assert children_names == ["sfo", "rdu", "nyc", "atl"]