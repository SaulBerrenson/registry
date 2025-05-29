## Исправление проблем с таблицами в БД

Данный nuget сервер не может обрабатывать пакеты с длинными наименованиями, простейший фикс ниже

```sh
docker exec -it postgres psql -U baget -d baget -c "ALTER TABLE \"Packages\" ALTER COLUMN \"Version\" TYPE TEXT; ALTER TABLE \"Packages\" ALTER COLUMN \"Id\" TYPE TEXT; ALTER TABLE \"Packages\" ALTER COLUMN \"OriginalVersion\" TYPE TEXT; ALTER TABLE \"PackageTypes\" ALTER COLUMN \"Version\" TYPE TEXT; ALTER TABLE \"Packages\" ALTER COLUMN \"Description\" TYPE TEXT;"
```