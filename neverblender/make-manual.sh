#!/bin/sh
# Builds an XHTML file from the Docbook manual.
# Requires xsltproc and the docbook-xml DTD and XSL files.
# (Debian: apt-get install xsltproc docbook-xml docbook-xsl)
# Will also work with other xsl processors.
# $Id$

declare output=${1:-/tmp/manual.html}
declare stylesheet=/usr/share/sgml/docbook/stylesheet/xsl/nwalsh/xhtml/docbook.xsl

echo "Generating manual HTML file: $output"
echo "Using XSL: $stylesheet"
echo "(Please ignore warnings about loading DTD from network, it's disabled...)"
xsltproc -o $output --nonet $stylesheet manual.dbk

