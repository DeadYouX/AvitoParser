# Avito Отклики в Google Sheets

Этот скрипт на Python автоматизирует процесс сбора информации об откликах на вакансии с Avito и записи этих данных в Google Sheets. Он предназначен для периодического обновления информации в вашей таблице.

## Описание

Скрипт выполняет следующие действия:

1.  **Авторизация:**
    *   Использует `client_id` и `client_secret` для каждого аккаунта Avito для получения токена доступа.
    *   Сохраняет токены в файле `accounts.json` (изначальные данные аккаунтов можно указать в самом скрипте).
2.  **Сбор данных:**
    *   Запрашивает список вакансий, обновленных за последние 60 дней.
    *   Получает ID откликов на эти вакансии.
    *   Получает подробную информацию по каждому отклику (имя, телефон, тип отклика, название вакансии и ссылка на вакансию).
3.  **Обработка данных:**
    *   Очищает данные от дубликатов.
    *   Сортирует отклики по времени создания.
4.  **Запись в Google Sheets:**
    *   Использует `creds.json` (файл с учетными данными сервисного аккаунта Google) для доступа к Google Sheets API.
    *   Добавляет новые отклики в указанную таблицу.
    *   Создает лист (вкладку) в таблице для каждого аккаунта Avito.
    *   Пропускает дубликаты, если они уже есть в таблице.
5.  **Периодическое обновление:**
    *   Обновляет токен доступа каждые 20 часов.
    *   Обновляет информацию об откликах и записывает её в Google Sheets через заданный промежуток времени (по умолчанию 5 минут, настраивается в переменной `sleep_minutes`).

## Требования

Для работы скрипта необходимы следующие компоненты:

*   **Python 3.7+**
*   **Библиотеки Python:**
    *   `requests` (для HTTP-запросов к API Avito)
    *   `json` (для работы с JSON)
    *   `datetime` (для работы с датами)
    *   `schedule` (для периодического запуска)
    *   `dateutil` (для парсинга дат)
    *   `gspread` (для работы с Google Sheets API)
    *   `time` (для работы со временем)
    
    Вы можете установить необходимые библиотеки, используя `pip`:
    ```bash
    pip install requests schedule python-dateutil gspread oauth2client
    ```

*   **Google Service Account:**
    *   Необходимо создать сервисный аккаунт в Google Cloud Platform.
    *   Необходимо предоставить доступ к Google Sheets API.
    *   Загрузить файл `creds.json` с ключами сервисного аккаунта в корень проекта.
*   **Google Sheet:**
    *   Создать Google Sheet.
    *   Указать URL таблицы в переменной `sheet_name` в скрипте.

## Использование

1.  **Клонируйте** репозиторий:
    ```bash
    git clone <URL вашего репозитория>
    ```

2.  **Установите** необходимые библиотеки (см. раздел "Требования").
3.  **Создайте** или загрузите файл `creds.json` с ключами сервисного аккаунта Google в корень проекта.
4.  **Укажите** URL таблицы в переменной `sheet_name` в скрипте.
5.  **Добавьте** данные ваших Avito аккаунтов в виде `["Имя", "CLIENT_ID", "CLIENT_SECRET"]` в список `accounts` в скрипте. (Эти данные будут сохранены в `accounts.json`, и при следующем запуске их можно будет удалить из `accounts`).
6.  **Запустите** скрипт:
    ```bash
    python <имя_вашего_скрипта>.py
    ```

7.  **Проверьте** вашу Google таблицу, куда будет записываться информация об откликах.

## Переменные в скрипте

*   `sleep_minutes`: Задержка в минутах между обновлениями данных (по умолчанию 5).
*   `accounts`: Список аккаунтов Avito, данные которых будут использованы для сбора информации.
*   `sheet_name`: URL Google Sheets таблицы.

## Как это работает

1.  Скрипт считывает или создает файл `accounts.json`, где хранятся необходимые данные для доступа к API Avito, такие как `client_id`, `client_secret`, токен доступа и курсор для отслеживания последних откликов.
2.  При первом запуске скрипт пытается добавить новые аккаунты из переменной `accounts` в `accounts.json`.
3.  Для каждого аккаунта скрипт обновляет токен доступа (раз в 20 часов).
4.  Скрипт получает список ID вакансий, у которых были обновления за последние 60 дней, а затем получает список ID откликов на эти вакансии.
5.  Если есть новые отклики, то скрипт запрашивает детальную информацию о каждом отклике.
6.  Далее скрипт обрабатывает полученные данные и записывает их в Google Sheets.
7.  Скрипт запускается периодически через `schedule`, чтобы постоянно отслеживать новые отклики.

## Примечания

*   Убедитесь, что у вас есть доступ к API Avito и Google Sheets.
*   Вам может понадобиться изменить настройки сервисного аккаунта Google, если скрипт не будет работать должным образом.
*   Скрипт отслеживает дубликаты откликов, поэтому повторные вызовы не должны добавлять одни и те же данные в Google Sheets.
*   Начальные данные аккаунтов Avito можно указать в коде, но они будут сохранены в `accounts.json` и могут быть удалены в дальнейшем.
*   Файл `accounts.json` хранит в себе токен доступа, поэтому обеспечьте его безопасность.
