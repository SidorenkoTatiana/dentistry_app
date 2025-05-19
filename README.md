# dentistry_app

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:SidorenkoTatiana/dentistry_app.git
```

```
cd dentistry_app
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

```
source venv/Scripts/activate
(Для Linux: source venv/bin/activate)

```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Запустить проект:

```
cd ..
(из корневой директории)
streamlit run dentistry_app/app/main.py
```