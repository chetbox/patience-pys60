# Settings
APPDIR=./patience
APPNAME=Patience
VERSION=00.91
UID=0x2000D023
PY2SIS=../py2sisng/py2sisng.py

# requires genaif, bmconv and makesis in PATH
PY2SIS_COMMAND=$(PY2SIS) --appname=$(APPNAME) --caption=$(APPNAME) --shortcaption=$(APPNAME) --version=$(VERSION) --uid=$(UID) --lang=EN --verbose $(APPDIR)


all :
	make patience.sis
	make patience-presdk20.sis
	make source.zip
	@echo "make complete."

cleanup :
	@echo "Deleting backup files from source..."
	rm -fv $(APPDIR)/*~

clean :
	@echo "Deleting old builds..."
	rm -fv patience.sis
	rm -fv patience-presdk20.sis
	rm -fr source.zip

patience.sis : $(APPDIR)/*.py $(APPDIR)/*.txt
	@echo "Creating .sis file..."
	make cleanup
	$(PY2SIS_COMMAND) patience.sis

patience-presdk20.sis : $(APPDIR)/*.py $(APPDIR)/*.txt
	@echo "Creating pre-SDK 2.0 .sis file..."
	make cleanup
	$(PY2SIS_COMMAND) --presdk20 patience-presdk20.sis

source.zip : $(APPDIR)/*.py $(APPDIR)/*.txt
	@echo "Packaging source..."
	make cleanup
	zip -r source.zip $(APPDIR)
