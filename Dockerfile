# Используем официальный образ PostgreSQL
FROM postgres:13.3

# Устанавливаем окружение
ENV POSTGRES_USER=postgres
ENV POSTGRES_DB=postgres
ENV POSTGRES_PASSWORD=0706

# Копируем DDL и DML файлы в директорию инициализации PostgreSQL init-scripts
COPY ./migrations/DDL.sql /docker-entrypoint-initdb.d/
COPY ./migrations/DML.sql /docker-entrypoint-initdb.d/

# Открываем порт
EXPOSE 5432


# toRun
# docker build -t db_init . 
# docker run --name cp -d -p 5432:5432 db_init