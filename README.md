# Squash ladder

Simple UI for manipulating a squash ladder divided into divisions.

INSTALL
=======

For Apache (>= 2.4) you may use the following template config:

```
<IfModule mod_ssl.c>
<VirtualHost *:443>
...
	Alias /squash /opt/squash/web
	<Directory /opt/squash/web/>
		AddHandler cgi-script .cgi
		Options +ExecCGI
		AllowOverride None
		Require all granted
	</Directory>
...
</VirtualHost>>
```

The alias directive tells Apache where to find the web directory. The
directory must have CGI support enabled. `mod_cgid` or similar must
also be enabled in the server.

To actually run the site, you also need a database. A database can be
downloaded from another site, like https://davve.net/squash/dump.cgi.
Unzip the file from the root repo to populate the `data/` directory.
Make sure the `data/` directory is read/writable by the user
running the web server, e.g. `www-data` on Debian based systems.

Other web servers should be configured correspondingly.

After restarting your server, you may then navigate your browser to
https://<hostname>/squash to browser the site.
