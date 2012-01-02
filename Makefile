
html: web/index.html

web/index.html: index.txt
	asciidoc -o ./web/index.html index.txt
