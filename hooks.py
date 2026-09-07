"""MkDocs hooks for building this site.

Both hooks here correct mkdocs-section-index, which `mkdocs.yml` enables so a
workspace's label in the navigation links to its `README.md` overview instead
of sitting beside it as a second row. One hook keeps
`mkdocs build --strict`, which AGENTS.md requires after any change under
`learning/`, usable with the plugin enabled. The other stops the plugin from
folding a section that has no overview to fold.
"""

import logging

from mkdocs.structure.nav import Section
from mkdocs.structure.pages import Page
from mkdocs_section_index import SectionPage

_SECTION_INDEX_LOGGER = "mkdocs.plugins.mkdocs_section_index.plugin"
_UNDETECTED_THEME = "couldn't detect a supported theme to adapt"


class _DropUndetectedThemeWarning(logging.Filter):
    """Silence one known-false warning from mkdocs-section-index.

    The plugin decides whether a theme is supported by matching template file
    paths against a hardcoded list of the themes it patches, which no
    third-party theme is on. So it always warns that it "couldn't detect a
    supported theme", even when the theme renders section index pages
    natively, as `primer` does. Under `--strict` that one warning aborts the
    build. Anything else the plugin logs still gets through.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        return _UNDETECTED_THEME not in record.getMessage()


logging.getLogger(_SECTION_INDEX_LOGGER).addFilter(_DropUndetectedThemeWarning())


def _unfold_sections_without_index(items: list, parent: Section | None) -> None:
    """Give a wrongly folded page its own navigation row back.

    mkdocs-section-index chooses what to fold by testing whether the section's
    first child already has a title: `if not page.title and page.url`. That is
    the right test for a hand-written `nav`, where a page carries a title from
    the start only because the configuration named it. It is no test at all
    here. Navigation is generated, from `learning/.nav.yml` and then from
    filenames, so nothing names a page, and `Page.title` stays empty until the
    page's source is read, which happens after `on_nav`. Every section's first
    child passes.

    In a workspace directory that is the intended result: the first child is
    the `README.md` overview, and folding it is why the plugin is enabled. In
    `lessons/` and in `reference/` there is no index page, so the plugin folded
    lesson 0001 and the first reference sheet instead. Each vanished from the
    sidebar and its label, `Lessons` or `Reference`, became a link to it, which
    is also why `Lessons` could never be the lesson list the reader expects.
    That list is the `## Lessons` table on the topic page.

    So undo the fold wherever the folded page is not an index page. Reverse it
    rather than prevent it: a hook is appended to the plugin collection, so its
    `on_nav` runs after every plugin's, and the state to restore is recorded on
    the object the plugin rewrote. Rewrite the same object back, because
    `nav.pages` and `File.page` both still point at it.
    """
    for i, item in enumerate(items):
        if isinstance(item, SectionPage) and item.file.name != "index":
            # The plugin moved the page's former peers onto it. Hand them to a
            # fresh section, with the page itself back in front of them, and
            # put that section where the page now stands.
            section = Section(title=item.title, children=[item, *item.children])
            section.parent = parent
            # `title` is a `weak_property`, meaning a plain descriptor that any
            # instance attribute shadows. The plugin set one, to the section's
            # title; deleting it lets the page derive its own title from its
            # front matter again. `is_section` and `is_page` are class
            # attributes on `Page`, and the plugin set both to True on the
            # instance, so deleting those two restores the class values too.
            item.__class__ = Page
            del item.title
            del item.is_section
            del item.is_page
            item.children = None
            for child in section.children:
                child.parent = section
            items[i] = section
            _unfold_sections_without_index(section.children, section)
        elif item.children:
            _unfold_sections_without_index(item.children, item)


def on_nav(nav, config, files):
    """Correct the navigation mkdocs-section-index just rewrote."""
    _unfold_sections_without_index(nav.items, None)
    return nav
