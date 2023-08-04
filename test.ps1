Push-Location $PSScriptRoot
Remove-Item test/res -Recurse -Force -ea SilentlyContinue
mkdir test/res -Force 
python merge.py test/eva.png test/a4.pdf -of test/res/a4.pdf     -r 90
python merge.py test/eva.png test/a3.pdf -of test/res/a3.pdf  -r 90
python merge.py test/eva.png test/10x10.pdf -of test/res/10.pdf -r 90