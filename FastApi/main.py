#!/bin/env python
from fastapi import FastAPI, File, UploadFile, HTTPException
import requests
from requests import Response
from fastapi.exceptions import ErrorList
from fastapi.responses import PlainTextResponse
import json
import uvicorn
from shemas import Group, Members, Site, User
from auth import get_new_ticket
from finder import get_full_userdata_by_id, get_user_by_email, get_user_by_login, get_users_by_site_id, get_user_groups_by_login
from file_dowloader import get_files
import re

app = FastAPI(debug=True)
head = get_new_ticket()
BASE_URL = "http://84.201.164.96:8080/alfresco/api/-default-/public/alfresco/versions/1"


def make_data(data):
    data_body = {
        "id": data["login"],
        "firstName": data["first_name"],
        "lastName": data["last_name"],
        "email": data["email"],
        "password": data["password"],
        "description": data["id"],
        "properties": {
        }
    }
    return data_body


@app.get("/api/v1/users", status_code=200)
def get_users(id: str = None, login: str = None, email: str = None):
    """Метод получения данных о пользователе по известным данным

    Keyword Arguments:
        id {str} -- telegramm id (default: {None})
        login {str} -- alfresco login (default: {None})
        email {str} -- email (default: {None})
        site_id {str} -- site_id (default: {None})

    Raises:
        HTTPException: 404 -- Пользователь не найден

    Returns:
    user data:
        [dict] -- {
            "id": "sring",
            "first_name": "sring",
            "last_name": "sring",
            "login": "sring",
            "email": "sring",
            "is_admin": bool,
            "group": [
                {
                    "id": "sring",
                    "name": sring or null
                }
            ]
        }
    """
    user_id = id
    is_admin = False
    group_list = []
    if user_id:
        user_data = get_full_userdata_by_id(id)
        if user_data:
            groups_user = get_user_groups_by_login(user_data["id"])
            for atrs in groups_user:
                group = {
                    "id": atrs["entry"]["id"],
                    "name": None
                }
                s = re.match(r".+-\d+_SiteManager", group["id"])
                if s:
                    group_managers = s[0].split("-")[-1]
                    if group_managers == f"{id}_SiteManager":
                        is_admin = True
                if "entry" in atrs and "displayName" in atrs["entry"]:
                    group["name"] = atrs["entry"]["displayName"]
                group_list.append(group)
            result = change_data_user(user_data, is_admin, group_list)
            return result
        raise HTTPException(status_code=404)
    if email:
        user_data = get_user_by_email(email)
        if user_data:
            groups_user = get_user_groups_by_login(user_data["id"])
            for atrs in groups_user:
                group = {
                    "id": atrs["entry"]["id"],
                    "name": None
                }
                s = re.match(r".+-\d+_SiteManager", group["id"])
                if s:
                    group_managers = s[0].split("-")[-1]
                    if group_managers == f"{id}_SiteManager":
                        is_admin = True
                if "entry" in atrs and "displayName" in atrs["entry"]:
                    group["name"] = atrs["entry"]["displayName"]
                group_list.append(group)
            result = change_data_user(user_data, is_admin, group_list)
            return result
        raise HTTPException(status_code=404)
    if login:
        user_data = get_user_by_login(login)
        if user_data:
            groups_user = get_user_groups_by_login(user_data["id"])
            for atrs in groups_user:
                group = {
                    "id": atrs["entry"]["id"],
                    "name": None
                }
                s = re.match(r".+-\d+_SiteManager", group["id"])
                if s:
                    group_managers = s[0].split("-")[-1]
                    if group_managers == f"{id}_SiteManager":
                        is_admin = True
                if "entry" in atrs and "displayName" in atrs["entry"]:
                    group["name"] = atrs["entry"]["displayName"]
                group_list.append(group)
            result = change_data_user(user_data, is_admin, group_list)
            return result
        raise HTTPException(status_code=404)


def change_data_user(data, is_admin=False, groups=None):
    """Метод перевода данных в данные согласно АПИ


    Arguments:
        data {dict} -- Карточка пользователя из alfresco

    Keyword Arguments: -- Значения по умолчанию так как возможно буду звать из другого места
        is_admin {bool} -- Является ли админом (default: {False})
        groups {list} -- Список групп (default: {None})

    Returns:
        [dict] -- Отформатированные данные
    """
    user = {
        "id": data["description"],
        "first_name": data["firstName"],
        "last_name": data["lastName"],
        "login": data["id"],
        "email": data["email"],
        "is_admin": is_admin,
        "group": groups
    }
    return user



@app.post("/api/v1/users", status_code=201)
def post_user(item:User):
    """
    создается админская запись 
    создается группа 
    запись добавляется в группу
    """
    # item.password = item.login + "123"
    data = make_data(item.__values__)

    global head
    make_user = requests.post(BASE_URL + "/people", headers=head, json=data)
    if make_user.status_code == 401:
        head = get_new_ticket()
        make_user = requests.post(BASE_URL + "/people", headers=head, json=data)
    if make_user.status_code == 201:
        print(f"make user status code {make_user.status_code}")
        body = {
            "id": "GROUP_" + item.login ,
            "displayName": "GROUP_" + item.login,
            "parentIds":[]
        }
        resp = requests.post(BASE_URL + "/groups", headers=head, json=body)
        print(resp.text)
        if resp.status_code == 201:
            user_data = {
            "id": item.login,
            "memberType": "PERSON"
            }
            group = "GROUP_" + item.login
            response = requests.post(BASE_URL + f"/groups/{group}/members", headers=head, json=user_data)
            print(response.text)
    if make_user.status_code == 409:
        print(f"make user status code {make_user.status_code}")
        raise HTTPException(status_code=409, detail="user exist")
    print(f"make user status code {make_user.status_code}")
    resp = json.loads(resp.text)["entry"]
    item.group["id"] = resp["id"]
    item.group["name"] = resp["id"]
    return item
        

@app.post("/api/v1/sites")
def add_site(item:dict, status_code=201):
    """
    создание сайта 
    """
    global head
    count = 1
    data = Site()
    login = get_full_userdata_by_id(item["owner_tid"])["id"]
    while True:
        number = str(count)
        data.id = "SITE" + number + "-" + item["owner_tid"]
        data.title = item["site_name"]
        response = requests.post(BASE_URL + "/sites", headers=head, json=dict(data))
        if response.status_code == 201:
            break
        count +=1
    if response.status_code == 201:
        print(response.text)
        print(f"add site status code {response.status_code}")
        shema = {
            "role": "SiteManager",
            "id": login
        }
        siteId = data.id
        requests.post(BASE_URL + f"/sites/{siteId}/members", headers=head, json=shema)
    delete_admin_from_site = requests.delete(BASE_URL + f"/people/api_user/sites/{siteId}", headers=head)
    print(delete_admin_from_site.status_code, "admin deleted")
    print(f"add site status code {response.status_code}")
    response_data = json.loads(response.text)["entry"]
    resp = {
        "id":response_data["id"],
        "name":response_data["title"],
        "guid":response_data["guid"]
    }
    return resp


@app.get("/api/v1/sites", status_code=200)
def get_sites(owner_id: str = None):
    """Получение списка сайтов (проектов) пользователя по его  id

    Arguments:
        owner_id {str} -- telegramm id

    Raises:
        HTTPException: 400 -- не получен дата сет
        HTTPException: 400 -- нет id пользователя
        HTTPException: 404 -- нет сайтов у пользователя

    Returns:
        [list] -- [
            {
                "id": "SITE50977-1100293794",
                "name": "hello"
            }
        ]
    """
    global head
    # если пустое поле с owner_id
    if not owner_id:
        raise HTTPException(status_code=400)
    list_sites = []
    # получаем словарь всех сайтов с пользователями
    all_sites = requests.get(f"{BASE_URL}/sites?relations=members", headers=head)
    if all_sites.status_code == 401:
        head = get_new_ticket()
        all_sites = requests.get(f"{BASE_URL}/sites?relations=members", headers=head)
    # получаем логин пользователя
    login = get_full_userdata_by_id(owner_id)["id"]
    sites = json.loads(all_sites.text)["list"]["entries"]
    # ищем сайты где пользователь состоит в списке
    result = []
    for site in sites:
        if ("relations" in site
            and "members" in site["relations"]
            and "list" in site["relations"]["members"]
            and "entries" in site["relations"]["members"]["list"]
        ):
            users = site["relations"]["members"]["list"]["entries"]
            for user in users:
                if user["entry"]["id"] == login:
                    entry = {
                        "id": "",
                        "name": ""
                    }
                    entry["id"] = site["entry"]["id"]
                    entry["name"] = site["entry"]["title"]
                    result.append(entry)
    if result == []:
        raise HTTPException(status_code=404)
    return result


@app.post("/api/v1/sites/{site_id}/users", status_code=201)
def add_new_user(site_id: str, item: dict):
    """
    создание пользователя в проекте
    нужно добавить автоматическое добавление в группу админа
    """
    global head
    data = make_data(item)
    response_user = requests.post(BASE_URL + "/people", headers=head, json=data)
    if response_user.status_code == 401:
        head = get_new_ticket()
        response_user = requests.post(BASE_URL + "/people", headers=head, json=data)
    new_user = {
        "role": "SiteManager",
        "id": data["id"]
    }
    response = requests.post(BASE_URL + f"/sites/{site_id}/members", headers=head, json=dict(new_user))
    
    # data = {
    #     "id": item["id"],
    #     "memberType": "PERSON"
    # }
    # response_group = requests.post(BASE_URL + f"/groups/{group}/members", headers=head, json=dict(data))
    return response.status_code


@app.delete("/api/v1/sites/{id}", status_code=204)
def delete_site(id: str):
    """Метод удаления сайта

    Arguments:
        id {str} -- сайт id

    Raises:
        HTTPException: 404 - сайт не найден
        HTTPException: остальные ошибки

    Returns:
        None
    """
    global head
    response = requests.delete(f"{BASE_URL}/sites/{id}", headers=head)
    if response.status_code == 401:
        head = get_new_ticket()
        response = requests.delete(f"{BASE_URL}/sites/{id}", headers=head)
    if response.status_code == 404:
        raise HTTPException(status_code=404)
    if response.status_code != 204:
        raise HTTPException(status_code=response.status_code)


@app.get("/api/v1/sites/{site_id}/users", status_code=200)
def get_site_users(site_id: str):
    """Метод получения пользователей сайта (проекта)
    админ сайта фильтруется, так как метод отдает данные
    для интерфеса удаления пользователей сайта

    Arguments:
        site_id {str} -- Идентификатор сайта

    Raises:
        HTTPException: 404 -- на сайте нет пользователей
        HTTPException: 400 -- Неверный id сайта

    Returns:
        [list] -- [
            {
                "role": "SiteConsumer",
                "person": {
                    "firstName": "string",
                    "jobTitle": "string",
                    "emailNotificationsEnabled": false,
                    "description": "id",
                    "company": {},
                    "id": "login",
                    "enabled": true,
                    "email": "string"
                    },
                "id": "api_user"
            }]
    """
    global head
    siteId = site_id
    try:
        login = get_full_userdata_by_id(site_id.split("-")[-1])["id"]
    except BaseException:
        raise HTTPException(status_code=400, detail="Bad side id")
    response = requests.get(f"{BASE_URL}/sites/{siteId}/members", headers=head)
    if response.status_code == 401:
        head = get_new_ticket()
        response = requests.get(f"{BASE_URL}/sites/{siteId}/members", headers=head)
    users = json.loads(response.text)["list"]["entries"]
    list_users = [user["entry"] for user in users if user["entry"]["id"] != login]
    if list_users == []:
        raise HTTPException(status_code=404)
    return list_users


@app.post("/api/v1/documents")
def post_documents(site_id:str, user_id:str, file_url:str = None): #file:UploadFile = File(...)
    """
    размещение документа на сайте с метками создателя по ссылке на яндекс диск
    пока только в корневую папку
    """
    global head
    if file_url == None:
        return 400
    user = get_full_userdata_by_id(user_id)
    files_ya = get_files(file_url)
    get_folder_id = requests.get(BASE_URL + f"/sites/{site_id}/containers/documentLibrary", headers=head)
    if get_folder_id.status_code == 401:
        head = get_new_ticket()
        get_folder_id = requests.get(BASE_URL + "/sites/SITE9id/containers/documentLibrary", headers=head)
    folder_id = json.loads(get_folder_id.text)["entry"]["id"]
    print(f"Found folder id {folder_id}")
    files_result = []
    for one in files_ya:
        url = BASE_URL + f"/nodes/{folder_id}/children"
        payload = {'name': one["name"],
        'autoRename': 'true',
        'cm:title': one["name"],
        'cm:description': f'Добавил {user["firstName"]} {user["lastName"]}',
        'exif:manufacturer': 'Canon'}
        files = [
        ('filedata', open(one["path"],'rb'))
        ]
        response = requests.post(url, headers=head, data = payload, files = files)
        print(f"File write to site {response.status_code}")
        if response.status_code != 201:
            return response.status_code
        file_shema = {
            "title": one["name"],
            "file_url": file_url,
            "file": {
                "id": 0,
                "content": "string",
                "name": "string",
                "original_name": one["name"]
            }
        }
        files_result.append(file_shema)
    # site_folders = requests.get(BASE_URL + f"/sites/{site_id}/containers", headers=head)
    # site_folders = json.loads(site_folders.text)["list"]["entries"]
    # folders = []
    # for folder in site_folders:
    #     x = {
    #         "id": folder["entry"]["id"],
    #         "folderName": folder["entry"]["folderId"]
    #     }
    #     folders.append(x)
    body = {
        "id":user_id,
        "group_id":"None",
        "site_id":site_id,
        "tags":[
            {"id":0,
            "title": "string"
            }
        ]
    }
    raise HTTPException(status_code=201, detail=[body,files_result])
    # return body, files_result

@app.post("/api/v1/documents/file")
def post_document(site_id:str = None,  user_id:str = None,url:str = None, file: UploadFile = File(...)):
    """
    размещение документа на сайте с метками создателя по загруженному файлу
    пока только в корневую папку
    """
    if file.filename == '':
        if url == None:
            raise HTTPException(status_code=201, detail="Item not found")

    global head
    user = get_full_userdata_by_id(user_id)
    print("get user data done")
    get_folder_id = requests.get(BASE_URL + f"/sites/{site_id}/containers/documentLibrary", headers=head)
    if get_folder_id.status_code == 401:
        head = get_new_ticket()
        get_folder_id = requests.get(BASE_URL + f"/sites/{site_id}/containers/documentLibrary", headers=head)
    print("get folder id done")
    folder_id = json.loads(get_folder_id.text)["entry"]["id"]

    print(f"Found folder id {folder_id}")
    url = BASE_URL + f"/nodes/{folder_id}/children"
    payload = {'name': file.filename,
        'autoRename': 'true',
        'cm:title': file.filename,
        'cm:description': f'Добавил {user["firstName"]} {user["lastName"]}',
        'exif:manufacturer': 'Canon'}
    files = [
        ('filedata', file.file.read())
    ]
    response = requests.post(url, headers=head, data = payload, files = files)
    print(f"File write to site {response.status_code}")
    if response.status_code != 201:
        return response.status_code
    return response.status_code


@app.get('/api/v1/site_documents')
def get_all_documents(site_id:str = None):
    """
    получение списка файлов из корневой папки сайта
    исключения обработаны
    """
    global head
    if site_id == None:
        raise HTTPException(status_code=400)
    result = []
    response = requests.get(BASE_URL + "/sites", headers=head)
    if response.status_code == 401:
        head = get_new_ticket()
        response = requests.get(BASE_URL + "/sites", headers=head)
    try:        
        sites = json.loads(response.text)["list"]["entries"]
        site_node = ""
        for site in sites:
            if site["entry"]["id"] == site_id:
                site_node = site["entry"]["guid"]
                break
        response = requests.get(BASE_URL + f"/nodes/{site_node}/children", headers=head)
        base_folder_id = json.loads(response.text)["list"]["entries"][0]["entry"]["id"]
        response = requests.get(BASE_URL + f"/nodes/{base_folder_id}/children", headers=head)
        files = json.loads(response.text)["list"]["entries"]
        for data in files:
            x = {
                "file_name": data["entry"]["name"],
                "id": data["entry"]["id"]
            }
            result.append(x)
        return result
    except:
        raise HTTPException(status_code=404)


@app.delete("/api/v1/documents/{id}", status_code=204)
def delete_document(id:str = None):
    """
    удаление файла по его id 
    """
    global head
    response = requests.delete(f"{BASE_URL}/nodes/{id}", headers=head)
    if response.status_code == 401:
        head = get_new_ticket()
        response = requests.delete(f"{BASE_URL}/nodes/{id}", headers=head)


@app.delete("/api/v1/users", status_code=204)
def delete_user(
    site_id: str, user_id: str = None,
    login: str = None, email: str = None
):
    """Метот удаления пользователя
    -деактивация учетной записи
    -удаление пользователя из сайта (проекта)

    Arguments:
        site_id {str} -- ID сайта

    Keyword Arguments:
        user_id {str} -- ID пользователя (default: {None})
        login {str} -- Login пользователя (default: {None})
        email {str} -- Email пользователя (default: {None})
        status_code {int} -- статус код ответа  (default: {204})

    Raises:
        HTTPException: 404 -- нет такого пользователя
    """
    if user_id:
        login = get_full_userdata_by_id(user_id)
        if login is not None:
            login = login["id"]
    if email:
        login = get_user_by_email(email)
        if login is not None:
            login = login["id"]
        global head
    payload = "{\"enabled\": false}\n"
    response = requests.put(f"{BASE_URL}/people/{login}", data=payload, headers=head)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=json.loads(response.text))
    if response.status_code == 401:
        head = get_new_ticket()
        response = requests.put(f"{BASE_URL}/people/{login}", data=payload, headers=head)
    response = requests.delete(f"{BASE_URL}/people/{login}/sites/{site_id}", headers=head)
    if response.status_code == 400:
        raise HTTPException(status_code=400, detail="Невозможно удалить единственного менеджера")


@app.get("/api/v1/document", status_code=200)
def get_user1(search_string:str = None):
    """получение данных о пользователе по id, мылу, почте , и список юзеров в проекте 
    обработал исключения 
    """
    return search_string, "Метод поиска по строке"


@app.put("/api/v1/users/{login}", status_code=200)
def update_user(login: str, data: dict = None):
    """Метод обновления информации пользователя по его логину

    Arguments:
        login {str} -- login

    Keyword Arguments:
        data {dict} -- {"id":"str" or "int"} (default: {None})
        status_code {int} -- (default: {200})

    Raises:
        HTTPException: 404 -- неверный login
        HTTPException: 400 -- неверный формат данных , нет данных

    Returns:
        {json} -- обновленная карточка пользователя
    """
    global head
    if data:
        new_data = {
            "description": str(data["id"])
        }
        response = requests.put(BASE_URL + f"/people/{login}", headers=head, json=new_data)
        if response.status_code == 401:
            head = get_new_ticket()
            response = requests.put(BASE_URL + f"/people/{login}", headers=head, json=new_data)
    if response.status_code == 200:
        response_data = json.loads(response.text)
        return response_data
    if response.status_code == 404:
        raise HTTPException(status_code=404)
    raise HTTPException(status_code=400)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

