"""Write an export file using a docx template.

:author: Shay Hill
:created: 2023-02-03
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

from docx2python import docx2python
from docx2python.attribute_register import Tags
from docx2python.utilities import replace_root_text
from lxml import etree

from todoist_export.paths import TEMPLATES

if TYPE_CHECKING:
    from collections.abc import Iterable

    from lxml.etree import _Element as EtreeElement  # type: ignore


TEMPLATE: Path = TEMPLATES / "sptc.docx"


def fix_template(template: Path):
    """Open and close template to join any broken runs.

    :param template: Path to template.docx file

    Docx2Python DocxReader joins runs that are separated by autocorrect entries,
    timestamps, etc. It is likely that any hand-created template will have such
    broken runs. It is only necessary to run this once to fix a template.
    """
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_path = Path(tmp.name)
        with docx2python(template).docx_reader as reader:
            reader.save(tmp_path)
    template.unlink()
    _ = Path(tmp_path).rename(template)


class ItemInserter:
    """Replace text in a clone of an element, then insert it into a parent element.

    A typical use case for this would be a table row with cells filled with marker
    text (patterns). __init__ would create a pattern from an element, then remove
    that element from its parent--so only one instance of `ItemInserter` can be
    created for a given element.

    When `ItemInserter` instance is called, a copy of the element is created, its
    pattern strings are replaced, and it is, by default, inserted back into the
    original parent of `self._elem` in the same place from which `self._elem` was
    removed. This insertion is negative indexed (or `sys.maxsize` if `self._elem` was
    the last element in `parent`), so an instance of `ItemInserter` created from a
    table row can be called several times, with each call adding a new row after the
    first.

    This will all work by itself, unless there are more than one `ItemInserter`
    instances created from elements of the same parent, then the indexes will not be
    able to automatically keep up with multiple calls. Or, you may want to create a
    catalog of ElemInserters for different paragraph styles and insert them somewhere
    else besides where you found them. In either case, a parent and index can be
    specified as arguments to `__call__`.

    The `clone` function is also public to create a clone (with `patterns` exchanged
    for `values` to be used however you like.

    `__call__` returns the clone inserted, so the parent and index of that clone can
    be inferred and tricky things can be done with insertion indices outside of the
    `ItemInserter` instance.
    """

    def __init__(self, elem: EtreeElement, patterns: Iterable[str]) -> None:
        """Create an `ItemInserter` from an element and a list of patterns.

        :param elem: The element to be cloned and inserted.
        :param patterns: A list of patterns to be replaced with values.
        """
        self._elem = elem
        self._patterns = tuple(patterns)

        self._parent = elem.getparent()
        self._index = sys.maxsize
        if self._parent is not None:
            self._parent.remove(elem)

    @property
    def parent(self) -> EtreeElement | None:
        """The original parent of self._elem.

        :return: The original parent of self._elem, this may be None.

        Only a document's root element won't have a parent. Even that can
        theoretically be used if a `parent` argument is given for `__call__`.
        `__call__` will only ask for this if no `parent` property if no `parent`
        arguemnt is given to `__call__`. If that happens, and `self._parent` is None,
        then no parent exists anywhere and a clone of `self._elem` cannot be
        inserted.
        """
        return self._parent

    def clone(self, values: Iterable[str]) -> EtreeElement:
        """Clone self._elem with patterns replaced with values.

        :param values: values which will replace self._patterns
        :return: a clone of self._elem with patterns replaced with values
        """
        elem_clone = etree.fromstring(etree.tostring(self._elem))
        for pattern, value in zip(self._patterns, values):
            replace_root_text(elem_clone, pattern, value)
        return elem_clone

    def __call__(
        self,
        values: Iterable[str],
        parent: EtreeElement | None = None,
        index: int | None = None,
    ) -> EtreeElement:
        """Replace patterns with values in `self._elem` and insert into parent element.

        :param values: strings to replace patterns in `self._elem`
        :param parent: optionally give parent element, defaults to `self._elem.parent`
        :param index: optionally give index in parent at which clone of `self.elem`
            will be inserted, defaults to original index (negative) of `self._elem`
            in `self._elem.parent`.
        :returns: returns clone of `self._elem` inserted into parent.
        :raise ValueError: if `values` is not the same length as `self._patterns
        :raise ValueError: if pattern elem has no `parent` and no parent given to call.
        """
        values_ = tuple(values)
        if len(values_) != len(self._patterns):
            msg = (
                "values must be same length as patterns: "
                + f"{len(values_)} != {len(self._patterns)}"
            )
            raise ValueError(msg)
        if index is None:
            index = self._index
        elem_clone = self.clone(values_)

        target = parent or self.parent
        if target is not None:
            target.insert(index, elem_clone)
        else:
            msg = "parent must be given if self._elem has no parent"
            raise ValueError(msg)
        return elem_clone


def _has_text(root: EtreeElement, text: str) -> bool:
    """Does any descendent element of :root: contain :text:?.

    :param root: an etree Element
    :param text: text to search for in root descendents.
    :returns: True if any descendent element contains :text:.
    """
    return any(text in (x.text or "") for x in root.iter())


def _find_text(root: EtreeElement, text: str, tag: str) -> EtreeElement:
    """Find next descendent element that contains :text: and has tag :tag:.

    :param root: etree.Element that presumably contains a descendent element with :text:
    :param text: text in table that will identify elem
    :param _tag: type of element sought
    :returns: elem.tag == :tag: and has_text(:text:)
    :raise ValueError: if no matching element can be found
    """
    try:
        return next(x for x in root.iter() if x.tag == tag and _has_text(x, text))
    except StopIteration as err:
        msg = f"{text} not found in {tag} element in {root}"
        raise ValueError(msg) from err


def write_wip(output_filename: Path | str, table: list[tuple[str, str, str]]):
    """Write a list of todos grouped by section.

    :param output_filename: name of the output file
    :param table: a list of tuples (section, project, task)
    :effect: writes a docx file to the current directory
    """
    reader = docx2python(TEMPLATE).docx_reader
    root = reader.file_of_type("officeDocument").root_element

    section_elem = _find_text(root, "$SECTION$", Tags.PARAGRAPH)
    project_elem = _find_text(root, "$PROJECT$", Tags.PARAGRAPH)
    task_elem = _find_text(root, "$TASK$", Tags.PARAGRAPH)
    # comment_elem = _find_text(root, "$COMMENT$", Tags.PARAGRAPH)

    add_section = ItemInserter(section_elem, ["$SECTION$"])
    add_project = ItemInserter(project_elem, ["$PROJECT$"])
    add_task = ItemInserter(task_elem, ["$TASK$"])

    last_section = "No Section"
    last_project = ""
    for section, project, task in table:
        if section != last_section:
            _ = add_section([section])
            last_section = section
            last_project = ""
        if project != last_project:
            _ = add_project([project])
            last_project = project
        _ = add_task([task])

    reader.save(output_filename)

if __name__ == "__main__":
    write_wip("test.docx", [("Section", "Project", "Task")])
