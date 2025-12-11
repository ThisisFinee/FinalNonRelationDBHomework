## Итоговое задание по модулю 2(NoSQL)
### Первичные требования:
+ Наличие Docker
### Примечания:
+ .env файл был оставлен специально для удобства
+ poetry.lock файл был оставлен специально для удобства
### Запуск бд и заполнение данными
#### 1. Собираем образ
```bash
docker build -t university-mongo .
```    
#### Запускаем MongoDB-контейнер
```bash
docker run -d \
  --name university-mongo \
  --env-file .env \
  -p 27017:27017 \
  -v mongo-data:/data/db \
  university-mongo
```    
#### Запускаем сидер(для обогащения бд данными) 
```bash
docker exec -it university-mongo poetry run python run_seed.py
```    
