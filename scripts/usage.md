# Примеры использования vcpkg_manager.py

# 1. Использование с настройками по умолчанию (локальный кеш)
python3 vcpkg_manager.py

# 2. Использование удаленного кеша с настройками по умолчанию
python3 vcpkg_manager.py --cache remote

# 3. Кастомное имя архива
python3 vcpkg_manager.py --archive my_project_deps_v2

# 4. Кастомный триплет для статической сборки
python3 vcpkg_manager.py --triplet x64-linux-static

# 5. Использование собственного NuGet сервера
python3 vcpkg_manager.py --cache remote --nuget-url http://my-company-nuget.com/v3/index.json

# 6. Полная кастомизация
python3 vcpkg_manager.py --cache remote --triplet x64-windows-static --archive custom_build_v1 --nuget-url http://internal-nuget.local/v3/index.json

# 7. Предварительный просмотр команд (dry run)
python3 vcpkg_manager.py --dry-run --cache remote --archive test_build


# Примеры использования vcpkg_manager.py с поддержкой отдельных шагов

# 1. Выполнить все шаги (по умолчанию)
python3 vcpkg_manager.py

# 2. Только установить зависимости
python3 vcpkg_manager.py --steps install

# 3. Только экспортировать зависимости
python3 vcpkg_manager.py --steps export

# 4. Только очистить установленные зависимости
python3 vcpkg_manager.py --steps cleanup

# 5. Установить и экспортировать (пропустить очистку)
python3 vcpkg_manager.py --steps install export

# 6. Установить с кастомным триплетом
python3 vcpkg_manager.py --steps install --triplet x64-linux-static

# 7. Экспортировать с кастомным именем архива
python3 vcpkg_manager.py --steps export --archive my_custom_build_v1

# 8. Установить с удаленным кешем
python3 vcpkg_manager.py --steps install --cache remote