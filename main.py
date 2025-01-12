import json, requests, time, schedule
from datetime import datetime, timedelta
from dateutil import parser
#-----------------------------------------------------
#задержка в минутах, минимум 5 минут (каждые n минут информация будет обновляться)
sleep_minutes = 5
#Аккаунты в виде: ["Имя", "CLIENT_ID", "CLIENT_SECRET"]
#(После запуска программы новые добавятся в файл accounts.json и их можно удалять)
#Добавленные лучше удалять, чтобы программа не задерживалась на них
accounts = [
    ["name", "client_id", "secret-key"],
]
#Ссылка на таблицу
sheet_name = "https://docs.google.com/spreadsheets/d/"
#-----------------------------------------------------

def get_vacancy_ids(headers, updatedAtFrom):
    vacancys = []
    for i in range(10):
        params = {
            "page": i,
            "per_page": 100,
            "updatedAtFrom": updatedAtFrom,
        }
        req = requests.get('https://api.avito.ru/core/v1/items', headers=headers, params=params)
        vacancys += [str(res["id"]) for res in (json.loads(req.text))['resources']]
    return vacancys

def get_applications(headers, vacancyIds, updatedAtFrom, cursor):
    applies = []
    for i in range((len(vacancyIds)//100)+1):
        try:
            vacancyId = vacancyIds[100*i:100*(i+1)]
        except:
            vacancyId = vacancyIds[100*i:(len(vacancyIds)-(100*(i+1)))]
        params = {
            "vacancyIds": ','.join(vacancyId),
            "updatedAtFrom": updatedAtFrom,
        }
        if cursor != None: params["cursor"] = cursor
        req = requests.get('https://api.avito.ru/job/v1/applications/get_ids', headers=headers, params=params)
        applies += [id['id'] for id in json.loads(req.text)["applies"]]
    return applies

def get_applies_list(headers, ids):
    applies = []
    for i in range((len(ids)//100)+1):
        try:
            id = ids[100*i:100*(i+1)]
        except:
            id = ids[100*i:(len(ids)-(100*(i+1)))]
        data = {
            "ids": id
        }
        req = requests.post('https://api.avito.ru/job/v1/applications/get_by_ids', headers=headers, json=data)
        applies += (req.json()['applies'])
    return applies

def get_vacancy(headers, vacancy_id):
    data = {
        "fields": "title"
    }
    req = requests.get(f'https://api.avito.ru/job/v2/vacancies/{vacancy_id}', headers=headers, json=data)
    return json.loads(req.text)

def get_all_info(all_applies, headers):
    all_info = []
    unique_set = set()

    for j in range(len(all_applies)):
        name = all_applies[j]['applicant']["data"]['name']
        phone = all_applies[j]['contacts']["phones"][0]['value']
        vacancy = get_vacancy(headers, all_applies[j]['vacancy_id'])
        vacancy_title = vacancy['title']
        vacancy_url = "https://www.avito.ru" + vacancy['url']

        if all_applies[j]['type'] == 'by_phone':
            type_applie = 'Посмотрел номер'
        elif all_applies[j]['type'] == 'by_chat':
            type_applie = 'Откликнулся'
        else:
            type_applie = ''

        try:
            created_at = datetime.fromisoformat(all_applies[j]['created_at'].replace("Z", "+00:00"))
        except:
            created_at = parser.parse(all_applies[j]['created_at'])
        created_at_str = created_at.strftime("%d.%m.%Y")

        record = (created_at_str, name, phone, type_applie, vacancy_title, vacancy_url, created_at)

        if record not in unique_set:
            unique_set.add(record)
            all_info.append(list(record))

    all_info.sort(key=lambda x: x[6])
    all_info = [list(record[:-1]) for record in all_info]
    return all_info


import gspread
from oauth2client.service_account import ServiceAccountCredentials

def parse_to_google_sheets(all_info, title, sheet_name):
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
    client = gspread.authorize(creds)

    try:
        sheet = client.open_by_url(sheet_name).worksheet(title)
    except gspread.exceptions.WorksheetNotFound:
        sheet = client.open_by_url(sheet_name).add_worksheet(title, 10000, 10)
    sheet.update_acell('A1', "Дата отклика")
    sheet.update_acell('B1', "Имя кандидата")
    sheet.update_acell('C1', "Номер телефона")
    sheet.update_acell('D1', "Тип отклика")
    sheet.update_acell('E1', "Название вакансии")
    sheet.update_acell('F1', "Ссылка на вакансию")

    existing_records = sheet.get_all_values()

    existing_set = set(tuple(row) for row in existing_records[1:])

    new_values = [info for info in all_info if tuple(info) not in existing_set]

    if new_values:
        sheet.append_rows(new_values, value_input_option='USER_ENTERED')
    return len(new_values)

def refresh_token():
    with open('accounts.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    for i in range(len(data)):
        CLIENT_ID, CLIENT_SECRET = data["acc" + str(i)]["CLIENT_ID"], data["acc" + str(i)]["CLIENT_SECRET"]
        req = requests.post(f'https://api.avito.ru/token/?grant_type=client_credentials&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}')
        token = json.loads(req.text)
        data["acc" + str(i)]["TOKEN"] = token['access_token']

    with open('accounts.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def add_accounts(accounts):
    with open('accounts.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    for i in range(len(accounts)):
        new = False
        if accounts[i][1] not in [account["CLIENT_ID"] for account in data.values()] and accounts[i][2] not in [account["CLIENT_SECRET"] for account in data.values()]:
            new = True
        if new:
            data['acc' + str(len(data))] = {
                "NAME": accounts[i][0],
                "CLIENT_ID": accounts[i][1],
                "CLIENT_SECRET": accounts[i][2],
                "TOKEN": None,
                "CURSOR": None
            }

    with open('accounts.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def main():
    print("Поиск откликов...")
    with open('accounts.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    for i in range(len(data)):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {data['acc'+str(i)]['TOKEN']}",
        }
        all_applies = []
        updatedAtFrom = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")
        vacancyIds = get_vacancy_ids(headers, updatedAtFrom)
        if vacancyIds != 0:
            appliesIds = get_applications(headers, vacancyIds, updatedAtFrom, data['acc'+str(i)]['CURSOR'])
            if len(appliesIds) != 0:
                all_applies.append(get_applies_list(headers, appliesIds))
                data['acc'+str(i)]['CURSOR'] = appliesIds[-1]
                with open('accounts.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                all_applies = all_applies[0]
                all_info = get_all_info(all_applies, headers)
                print(f"Проверка {len(all_info)} откликов в таблицу {data['acc'+str(i)]['NAME']}.")
                len_new_values = parse_to_google_sheets(all_info, data['acc'+str(i)]['NAME'], sheet_name)
                print(f"В таблицу {data['acc'+str(i)]['NAME']} записано {len_new_values} откликов.")
    print("Поиск закончен.")


add_accounts(accounts)

refresh_token()
main()

schedule.every(20).hours.do(lambda: refresh_token())
schedule.every(sleep_minutes).minutes.do(lambda: main())

while True:
    schedule.run_pending()
    time.sleep(1)
