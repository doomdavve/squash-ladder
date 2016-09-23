FILES=index.html list.cgi load.cgi save.cgi dump.cgi tracker.py copy-to-new-format.py
HOST=davve.net
HOSTDIR=/opt/squash/
publish:
	scp $(FILES) $(HOST):$(HOSTDIR)

.PHONY: publish
