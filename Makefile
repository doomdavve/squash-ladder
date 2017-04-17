WEB_FILES=index.html player.html list.cgi load.cgi save.cgi dump.cgi \
	favicon.png style.css results.cgi main.js
PREFIXED_WEB_FILES=$(addprefix web/,$(WEB_FILES))
TOOL_FILES=tracker.py conv-db.py
PREFIXED_TOOL_FILES=$(addprefix tools/,$(TOOL_FILES))
HOST=davve.net
HOST_WEBDIR=/opt/squash/web
HOST_TOOLDDIR=/opt/squash/tools
publish:
	scp $(PREFIXED_WEB_FILES) $(HOST):$(HOST_WEBDIR)
	scp $(PREFIXED_TOOL_FILES) $(HOST):$(HOST_TOOLDDIR)

.PHONY: publish
