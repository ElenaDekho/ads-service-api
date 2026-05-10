import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("ТЕСТИРОВАНИЕ API ОБЪЯВЛЕНИЙ С АВТОРИЗАЦИЕЙ")
print("=" * 60)

# =========================================================
# 1. Создаём пользователей
# =========================================================
print("\n1. СОЗДАНИЕ ПОЛЬЗОВАТЕЛЕЙ")

# Создаём обычного пользователя
resp = requests.post(f"{BASE_URL}/user", json={
    "username": "regular_user",
    "password": "user123",
    "group": "user"
})
print(f"  Создан regular_user (группа user): {resp.status_code}")
if resp.status_code == 201:
    regular_user_id = resp.json()["id"]
    print(f"    ID: {regular_user_id}")
else:
    print(f"    Ошибка: {resp.text}")
    exit()

# Создаём администратора
resp = requests.post(f"{BASE_URL}/user", json={
    "username": "admin_user",
    "password": "admin123",
    "group": "admin"
})
print(f"  Создан admin_user (группа admin): {resp.status_code}")
if resp.status_code == 201:
    admin_user_id = resp.json()["id"]
    print(f"    ID: {admin_user_id}")
else:
    print(f"    Ошибка: {resp.text}")
    exit()

# Создаём второго обычного пользователя (чужого)
resp = requests.post(f"{BASE_URL}/user", json={
    "username": "other_user",
    "password": "other123",
    "group": "user"
})
print(f"  Создан other_user (чужой пользователь): {resp.status_code}")
if resp.status_code == 201:
    other_user_id = resp.json()["id"]
    print(f"    ID: {other_user_id}")
else:
    print(f"    Ошибка: {resp.text}")
    exit()

# =========================================================
# 2. Логинимся и получаем токены
# =========================================================
print("\n2. АВТОРИЗАЦИЯ")

# Логин обычного пользователя
resp = requests.post(f"{BASE_URL}/login", json={
    "username": "regular_user",
    "password": "user123"
})
print(f"  Логин regular_user: {resp.status_code}")
if resp.status_code == 200:
    regular_token = resp.json()["token"]
    print(f"    Токен получен: {regular_token[:20]}...")
else:
    print(f"    Ошибка: {resp.text}")
    exit()

# Логин администратора
resp = requests.post(f"{BASE_URL}/login", json={
    "username": "admin_user",
    "password": "admin123"
})
print(f"  Логин admin_user: {resp.status_code}")
if resp.status_code == 200:
    admin_token = resp.json()["token"]
    print(f"    Токен получен: {admin_token[:20]}...")
else:
    print(f"    Ошибка: {resp.text}")
    exit()

# Логин с неверным паролем (должна быть ошибка 401)
print("\n  ПРОВЕРКА НЕВЕРНОГО ПАРОЛЯ")
resp = requests.post(f"{BASE_URL}/login", json={
    "username": "regular_user",
    "password": "wrong_password"
})
print(f"    Неверный пароль: {resp.status_code} (ожидается 401)")
if resp.status_code == 401:
    print("    ✅ Ошибка 401 получена")
else:
    print(f"    ❌ Ожидался 401, получен {resp.status_code}")

# =========================================================
# 3. Проверка доступа без токена
# =========================================================
print("\n3. ДОСТУП БЕЗ ТОКЕНА (неавторизованный пользователь)")

# Получение пользователя по ID
resp = requests.get(f"{BASE_URL}/user/{regular_user_id}")
print(f"  GET /user/{regular_user_id}: {resp.status_code} (ожидается 200)")
if resp.status_code == 200:
    print("    ✅ Доступ разрешён")

# Поиск объявлений (пока пусто)
resp = requests.get(f"{BASE_URL}/advertisement")
print(f"  GET /advertisement: {resp.status_code} (ожидается 200)")
if resp.status_code == 200:
    print("    ✅ Поиск работает")

# Попытка создать объявление без токена (должна быть ошибка 401)
resp = requests.post(f"{BASE_URL}/advertisement", json={
    "title": "Неавторизованное объявление",
    "description": "Это объявление не должно создаться",
    "price": 100,
    "author": "anonymous"
})
print(f"  POST /advertisement без токена: {resp.status_code} (ожидается 401)")
if resp.status_code == 401:
    print("    ✅ Доступ запрещён (нужен токен)")

# =========================================================
# 4. Действия от имени обычного пользователя (regular_user)
# =========================================================
print("\n4. ДЕЙСТВИЯ ОТ ИМЕНИ regular_user (группа user)")
headers = {"x-token": regular_token}

# Создание объявления
resp = requests.post(f"{BASE_URL}/advertisement", json={
    "title": "Моё первое объявление",
    "description": "Продаю велосипед",
    "price": 5000,
    "author": "regular_user"
}, headers=headers)
print(f"  Создание объявления: {resp.status_code} (ожидается 201)")
if resp.status_code == 201:
    ad_id = resp.json()["id"]
    print(f"    Создано объявление с ID: {ad_id}")
else:
    print(f"    Ошибка: {resp.text}")
    exit()

# Получение своего объявления (доступно без токена)
resp = requests.get(f"{BASE_URL}/advertisement/{ad_id}")
print(f"  GET /advertisement/{ad_id} без токена: {resp.status_code} (ожидается 200)")
if resp.status_code == 200:
    print("    ✅ Объявление доступно без авторизации")

# Обновление своего объявления
resp = requests.patch(f"{BASE_URL}/advertisement/{ad_id}", json={
    "price": 4500
}, headers=headers)
print(f"  Обновление своего объявления: {resp.status_code} (ожидается 200)")
if resp.status_code == 200:
    print("    ✅ Объявление обновлено")

# Обновление своих данных
resp = requests.patch(f"{BASE_URL}/user/{regular_user_id}", json={
    "username": "regular_user_updated"
}, headers=headers)
print(f"  PATCH /user/{regular_user_id} (свои данные): {resp.status_code} (ожидается 200)")
if resp.status_code == 200:
    print("    ✅ Данные пользователя обновлены")

# =========================================================
# 5. Проверка прав (доступ к чужому объявлению)
# =========================================================
print("\n5. ПРОВЕРКА ПРАВ: ДОСТУП К ЧУЖОМУ ОБЪЯВЛЕНИЮ")

# Сначала создадим объявление от другого пользователя (other_user)
print("  Сначала создаём объявление от other_user...")
headers_other = {"x-token": requests.post(f"{BASE_URL}/login", json={
    "username": "other_user", "password": "other123"
}).json()["token"]}

resp = requests.post(f"{BASE_URL}/advertisement", json={
    "title": "Объявление другого пользователя",
    "description": "Это объявление принадлежит other_user",
    "price": 1000,
    "author": "other_user"
}, headers=headers_other)
other_ad_id = resp.json()["id"]
print(f"    Создано объявление other_user с ID: {other_ad_id}")

# Пытаемся обновить чужое объявление от regular_user (должна быть ошибка 403)
resp = requests.patch(f"{BASE_URL}/advertisement/{other_ad_id}", json={
    "price": 999
}, headers=headers)
print(f"  regular_user обновляет чужое объявление: {resp.status_code} (ожидается 403)")
if resp.status_code == 403:
    print("    ✅ Доступ запрещён (нельзя чужое)")
else:
    print(f"    ❌ Ожидался 403, получен {resp.status_code}")

# =========================================================
# 6. Действия от имени администратора
# =========================================================
print("\n6. ДЕЙСТВИЯ ОТ ИМЕНИ admin_user (группа admin)")
admin_headers = {"x-token": admin_token}

# Администратор обновляет чужое объявление (должно быть разрешено)
resp = requests.patch(f"{BASE_URL}/advertisement/{other_ad_id}", json={
    "price": 777
}, headers=admin_headers)
print(f"  admin обновляет чужое объявление: {resp.status_code} (ожидается 200)")
if resp.status_code == 200:
    print("    ✅ Администратор может обновить чужое")

# Администратор удаляет чужое объявление
resp = requests.delete(f"{BASE_URL}/advertisement/{other_ad_id}", headers=admin_headers)
print(f"  admin удаляет чужое объявление: {resp.status_code} (ожидается 200)")
if resp.status_code == 200:
    print("    ✅ Администратор может удалить чужое")

# =========================================================
# 7. Проверка удаления пользователя
# =========================================================
print("\n7. УДАЛЕНИЕ ПОЛЬЗОВАТЕЛЯ")

# Обычный пользователь удаляет себя
resp = requests.delete(f"{BASE_URL}/user/{regular_user_id}", headers=headers)
print(f"  regular_user удаляет себя: {resp.status_code} (ожидается 200)")
if resp.status_code == 200:
    print("    ✅ Пользователь удалил себя")

# Попытка получить удалённого пользователя (должна быть ошибка 404)
resp = requests.get(f"{BASE_URL}/user/{regular_user_id}")
print(f"  GET удалённого пользователя: {resp.status_code} (ожидается 404)")
if resp.status_code == 404:
    print("    ✅ Пользователь действительно удалён")

# =========================================================
# 8. Проверка ошибки 403 при попытке удалить другого пользователя
# =========================================================
print("\n8. ПРОВЕРКА ОШИБКИ 403: ОБЫЧНЫЙ ПОЛЬЗОВАТЕЛЬ УДАЛЯЕТ ДРУГОГО")

# Сначала создадим токен для другого пользователя
headers_other = {"x-token": requests.post(f"{BASE_URL}/login", json={
    "username": "other_user", "password": "other123"
}).json()["token"]}

# Пытаемся удалить admin_user от имени other_user (должна быть 403)
resp = requests.delete(f"{BASE_URL}/user/{admin_user_id}", headers=headers_other)
print(f"  other_user пытается удалить admin_user: {resp.status_code} (ожидается 403)")
if resp.status_code == 403:
    print("    ✅ Доступ запрещён (нельзя удалять других)")
else:
    print(f"    ❌ Ожидался 403, получен {resp.status_code}")

# =========================================================
print("\n" + "=" * 60)
print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
print("=" * 60)