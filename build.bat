pyinstaller -y --windowed .\src\ArtStationDownloader.py
del dist\ArtStationDownloader.zip
7z a -tzip dist\ArtStationDownloader.zip dist\ArtStationDownloader
pyinstaller -y --windowed -F .\src\ArtStationDownloader.py
@pause