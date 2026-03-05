import random
from datetime import datetime, timedelta
import pandas as pd

# 1. Генератор тестовых транзакций
def generate_transactions(num=100):
    """
    Генерирует список случайных транзакций для тестирования.
    """
    transactions = []
    
    # Генерируем 10 пользователей
    users = [f'user_{i}' for i in range(1, 11)] 
    
    # Словарь стран
    countries = [
        'Russia', 'Kazakhstan', 'Belarus', 
        'Cyprus', 'Nigeria', 'Panama', # Допустим, эти три страны будут high_risk
        'United States', 'Germany', 'United Kingdom',
        'China', 'India', 'Brazil', 'United Arab Emirates'
    ] 
    
    base_time = datetime.now() - timedelta(hours=12) # Начинаем генерацию 12 часов назад 

    for i in range(num):
        # Генерируем время с шагом от 1 до 15 минут для имитации разной частоты
        t_offset = random.randint(1, 15)
        base_time += timedelta(minutes=t_offset)
        
        #Transaction
        tx = {
            'transaction_id': f'txn_{i+1:03d}', # 1. Уникальный номер (ID) транзакции
            'user_id': random.choice(users), # 2. Идентификатор пользователя
            'amount': round(random.uniform(500, 15000), 2), # Суммы перевода от 500 до 15000 у.е.
            'timestamp': base_time, # 4. Время проведения операции
            'merchant_country': random.choice(countries) # 5. Страна продавца
        }
        transactions.append(tx)

    return transactions

# 2. Детектор мошенничества с учётом регуляторного правила
def fraud_detection(transactions, amount_limit=10000, freq_limit=5, high_risk_countries=['Cyprus', 'Nigeria', 'Panama']):
    """
    Проверяет транзакции по правилам фрод-мониторинга.
    """
    results = []
    user_activity = {} # Словарь для отслеживания времени транзакций пользователя

    for tx in transactions:
        user_id = tx['user_id']
        amount = tx['amount']
        tx_time = tx['timestamp']
        country = tx['merchant_country']
        
        # Базовый статус
        status = "APPROVED"

        # Инициализация истории пользователя, если её нет
        if user_id not in user_activity:
            user_activity[user_id] = []

        # Проверка Правила 2 (Частота)
        # Очищаем старые транзакции (старше 1 часа от текущей)
        one_hour_ago = tx_time - timedelta(hours=1)
        user_activity[user_id] = [t for t in user_activity[user_id] if t >= one_hour_ago]
        
        # Добавляем текущую транзакцию
        user_activity[user_id].append(tx_time)
        
        # Если в течение часа это уже 6-я (или более) транзакция
        is_high_frequency = len(user_activity[user_id]) > freq_limit

        # Проверка Правила 1 (Лимит суммы) и Регуляторного требования
        current_limit = amount_limit
        is_high_risk_country = country in high_risk_countries

        # Снижение лимита в 2 раза для стран с высоким риском
        if is_high_risk_country:
            current_limit = amount_limit / 2.0

        is_high_amount = amount > current_limit

        # Назначение статусов
        # Приоритет блокировки выше, чем простого флага
        if is_high_amount and is_high_risk_country:
            status = "BLOCKED: High Risk Country & Amount"
        elif is_high_amount:
            status = "FLAGGED: High Amount"
        elif is_high_frequency:
            status = "FLAGGED: High Frequency"

        # Формируем результат
        results.append({
            'transaction_id': tx['transaction_id'],
            'user_id': user_id,
            'amount': amount,
            'country': country,
            'time': tx_time.strftime("%Y-%m-%d %H:%M:%S"),
            'status': status
        })

    return results

# 3. Запуск и вывод отчёта
if __name__ == "__main__":
    # Генерируем тестовые транзакции
    txns = generate_transactions(num=50) # Увеличим выборку для наглядности
    
    # Запускаем проверку. 
    risky = ['Cyprus', 'Nigeria', 'Panama']
    report = fraud_detection(txns, amount_limit=10000, freq_limit=5, high_risk_countries=risky)
    
    # Вывод результатов
    # Поля: ID (10), USER (10), AMOUNT (10), COUNTRY (22), TIME (20), STATUS
    header = f"{'TXN_ID':<10} | {'USER':<10} | {'AMOUNT':<10} | {'COUNTRY':<22} | {'TIME':<20} | {'STATUS'}"
    print(header)
    print("-" * len(header))
    
    for r in report:
        print(f"{r['transaction_id']:<10} | {r['user_id']:<10} | {r['amount']:<10.2f} | {r['country']:<22} | {r['time']:<20} | {r['status']}")

    # Сохраняем таблицу в файл Excel
    df = pd.DataFrame(report)
    filename = 'fraud_report.xlsx'
    df.to_excel(filename, index=False)
    print(f"\nОтчет успешно сохранен в файл: {filename}")