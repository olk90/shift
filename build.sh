#!/bin/zsh
pyinstaller -n "shift" \
  --add-data "ui/employeeEditor.ui:./ui" \
  --add-data "ui/employeeTypeEditor.ui:./ui" \
  --add-data "ui/employeeTypeView.ui:./ui" \
  --add-data "ui/employeeView.ui:./ui" \
  --add-data "ui/main.ui:./ui" \
  --add-data "ui/offPeriodAddDialog.ui:./ui" \
  --add-data "ui/offPeriodEditor.ui:./ui" \
  --add-data "ui/offPeriodView.ui:./ui" \
  --add-data "ui/optionsEditor.ui:./ui" \
  --add-data "ui/planningView.ui:./ui" \
  --add-data "ui/scheduleEditor.ui:./ui" \
  --add-data "translations/base_de.qm:./translations" \
  -D --clean main.py
