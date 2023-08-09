## Описание проекта

Проект доступен по адресу https://profoodgram.ddns.net/  
Доступ для администратора  
Логин: admin  
Пароль: admin1231  


Проект Foodgram позволяет пользователям поделиться своими любимыми рецептами и найти что-то новенькое для приготовления!
На сейте вы сможете:
- Зарегистрироваться.
- Добавить/отредактировать/удалить свой рецепт.
- Подписаться на авторов!
- Добавлять понравившиеся рецепты в избранное!
- Добавлять рецепты в список покупок.
- Скачивать список нужных ингредиентов!

## Технологии

- Python 3.9
- Django REST
- JavaScript
- Gunicorn
- Nginx
- Node.js
- PostgreSQL
- Docker

## Запуск проекта из образов с Docker hub

Для запуска необходимо создать папку проекта, например `foodgram` и перейти в нее:

```bash
mkdir foodgram
cd foodgram
```

В папку проекта скачиваем файл `docker-compose.production.yml` и запускаем его:

```bash
sudo docker compose -f docker-compose.production.yml up
```

Произойдет скачивание образов, создание и включение контейнеров, создание томов и сети.

## Запуск проекта из исходников GitHub

Клонируем себе репозиторий: 

```bash 
git clone git@github.com:Adelina1231/foodgram-project-react.git
```

Выполняем запуск:

```bash
sudo docker compose -f docker-compose.yml up
```

## После запуска: Миграции, сбор статистики

После запуска необходимо выполнить сбор статистики и миграции бэкенда. Статистика фронтенда собирается во время запуска контейнера, после чего он останавливается. 

```bash
sudo docker compose -f [имя-файла-docker-compose.yml] exec backend python manage.py migrate

sudo docker compose -f [имя-файла-docker-compose.yml] exec backend python manage.py collectstatic

sudo docker compose -f [имя-файла-docker-compose.yml] exec backend cp -r /app/collected_static/. /static/static/
```

И далее проект доступен на: 

```
http://localhost:8000/
```

## Остановка оркестра контейнеров

В окне, где был запуск **Ctrl+С** или в другом окне:

```bash
sudo docker compose -f docker-compose.yml down
```

## Автор

Аделина Тазиева https://github.com/Adelina1231

