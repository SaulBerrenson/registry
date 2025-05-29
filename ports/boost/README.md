## Подготовка новой версии архива

Минимальная версия 1.81.0 (для сборки чисто через cmake)

### Склонировать рекурсивно нужную версию
git clone -b boost-1.83.0 --recurse-submodules https://github.com/boostorg/boost boost-1-83-0
### Удалить все следы гита (размер слишком огромный)
cd boost-1-83-0
Remove-Item -Recurse -Force .git

### Заархивировать в ZIP с именем boost-1-83-0.zip

