FILES=index.html list.cgi load.cgi save.cgi
HOST=davve.net
HOSTDIR=squash/
publish:
	scp $(FILES) $(HOST):$(HOSTDIR)

.PHONY: publish
