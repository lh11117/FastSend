pyinstaller -D -w "main.py" -p user.py -p mainwindow.py -p setting.py -n "同网快传" --noconfirm

xcopy /Y /S "./pages" "dist/同网快传/pages"  /E /I /A