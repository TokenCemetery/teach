"""MkDocs hooks for building this site.

Both hooks here correct mkdocs-section-index, which `mkdocs.yml` enables so a
workspace's label in the navigation links to its `README.md` overview instead
of sitting beside it as a second row. One hook keeps
`mkdocs build --strict`, which AGENTS.md requires after any change under
`learning/`, usable with the plugin enabled. The other stops the plugin
folding a section that has no overview to fold, and gives every page it does
fold its own front-matter title back.
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


def _correct_folded_pages(items: list, parent: Section | None) -> None:
    """Undo the two things mkdocs-section-index gets wrong on generated nav.

    The plugin chooses what to fold by testing whether the section's first
    child already has a title: `if not page.title and page.url`. That is the
    right test for a hand-written `nav`, where a page carries a title this
    early only because the configuration named it. It is no test at all here.
    Navigation is generated, from `learning/.nav.yml` and then from filenames,
    so nothing names a page, and `Page.title` stays empty until the page's
    source is read, which happens after `on_nav`. Every section's first child
    passes. Having folded a page, the plugin then assigns it the section's own
    title, which for a generated nav is the directory name, capitalized.

    So there are two corrections, and every folded page needs the second one.

    Both work by rewriting the object the plugin rewrote, rather than by
    stopping it: a hook is appended to the plugin collection, so its `on_nav`
    runs after every plugin's. Rewriting the same object also keeps
    `nav.pages` and `File.page`, which both still point at it, in agreement
    with the tree.
    """
    for i, item in enumerate(items):
        if not isinstance(item, SectionPage):
            if item.children:
                _correct_folded_pages(item.children, item)
            continue

        # Hold on to what the plugin copied from the section, since the
        # section itself is gone and this is the only record of its title.
        section_title = item.title
        # Correction one, for every folded page. `Page.title` is a
        # `weak_property`, meaning a plain descriptor that any instance
        # attribute shadows, and the plugin set one. Deleting it puts the
        # page's own front matter back in charge of its title, in the sidebar
        # and equally in the browser tab, the social-card meta, the
        # breadcrumbs and the Previous/Next links.
        del item.title

        if item.file.name == "index":
            # The fold the plugin is enabled for: a workspace's label is its
            # `README.md` overview instead of a second row beside it.
            _correct_folded_pages(item.children, item)
            continue

        # Correction two. `lessons/` and `reference/` have no index page, so
        # the plugin folded lesson 0001 and the first reference sheet instead.
        # Each vanished from the sidebar and its label, `Lessons` or
        # `Reference`, became a link to it, which is also why `Lessons` could
        # never be the lesson list the reader expects. That list is the
        # `## Lessons` table on the topic page.
        #
        # The plugin moved the page's former peers onto it. Hand them to a
        # fresh section, with the page itself back in front of them, and put
        # that section where the page now stands.
        section = Section(title=section_title, children=[item, *item.children])
        section.parent = parent
        # `is_section` and `is_page` are class attributes on `Page`, and the
        # plugin set both to True on the instance, so deleting those two
        # restores the class values.
        item.__class__ = Page
        del item.is_section
        del item.is_page
        item.children = None
        for child in section.children:
            child.parent = section
        items[i] = section
        _correct_folded_pages(section.children, section)


def on_nav(nav, config, files):
    """Correct the navigation mkdocs-section-index just rewrote."""
    _correct_folded_pages(nav.items, None)
    return nav
