all: write_bones.py
	pyinstaller --onefile --icon=yakuza0.ico .\write_bones.py
	Xcopy /E /I .\ids .\dist\ids
	Xcopy /I .\data.csv .\dist\data.csv
