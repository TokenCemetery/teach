"""MkDocs hooks for building this site.

It exists so that `mkdocs build --strict`, which AGENTS.md requires after any
change under `learning/`, stays usable with mkdocs-section-index enabled.
"""

import logging

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
