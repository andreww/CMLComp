
html: web/index.html stds

stds: web/stds/CmlData.html web/stds/CmlParameters.html web/stds/DocumentStructure.html web/stds/FormalStandards.html web/stds/index.html web/stds/CmlMicroformats.html

web/index.html: index.txt
	asciidoc -o ./web/index.html index.txt

web/stds/CmlData.html: stds/CmlData.txt
	asciidoc -o ./web/stds/CmlData.html stds/CmlData.txt

web/stds/CmlParameters.html: stds/CmlParameters.txt
	asciidoc -o ./web/stds/CmlParameters.html stds/CmlParameters.txt

web/stds/DocumentStructure.html: stds/DocumentStructure.txt
	asciidoc -o ./web/stds/DocumentStructure.html stds/DocumentStructure.txt

web/stds/FormalStandards.html: stds/FormalStandards.txt
	asciidoc -o ./web/stds/FormalStandards.html stds/FormalStandards.txt

web/stds/index.html: stds/index.txt
	asciidoc -o ./web/stds/index.html stds/index.txt

web/stds/CmlMicroformats.html: stds/CmlMicroformats.txt
	asciidoc -o ./web/stds/CmlMicroformats.html stds/CmlMicroformats.txt
