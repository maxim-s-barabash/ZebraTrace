.PHONY: all

all: ui tr qm

ui: src/ui_build/mainwindow.ui src/ui_build/mainwindow.qrc
	@pyuic5 src/ui_build/mainwindow.ui -o src/zebratrace/gui/ui_mainwindow.py --from-imports
	@pyrcc5 src/ui_build/mainwindow.qrc -o src/zebratrace/gui/mainwindow_rc.py

tr:
	@pylupdate5 zebratrace.pro

qm: src/translations/*.ts
	@lrelease $?


