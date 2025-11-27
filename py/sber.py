import glob
import re
from datetime import datetime
from unidecode import unidecode
import fitz

PATH = '../input/sber'
FILENAMES = glob.glob(PATH + '/*.pdf')


def get_transactions():
    transactions = []

    for filename in FILENAMES:
        file = fitz.open(filename)

        for page in file:
            text = page.get_text()
            lines = [line.strip() for line in text.split('\n') if line.strip()]

            i = 0
            while i < len(lines) - 4:
                # Ищем дату операции (например: 23.11.2025)
                if re.match(r'\d{2}\.\d{2}\.\d{4}', lines[i]):
                    trans_date = lines[i]

                    # Проверяем следующую строку - может быть время или сразу категория
                    if i + 1 < len(lines) and ':' in lines[i + 1]:
                        trans_time = lines[i + 1]
                        # Пропускаем код авторизации (например: 686359)
                        if i + 3 < len(lines):
                            category = lines[i + 3]
                        else:
                            category = ""

                        # Сумма обычно через 1-2 строки после категории
                        amount_idx = i + 4
                        while amount_idx < len(lines) and amount_idx < i + 7:
                            if re.search(r'[+-]?\d[\d\s]*,\d{2}', lines[amount_idx]):
                                amount_str = lines[amount_idx]
                                break
                            amount_idx += 1
                        else:
                            amount_str = ""

                        # Описание может быть перед или после суммы
                        description = ""
                        for desc_idx in range(i + 2, min(i + 8, len(lines))):
                            if (desc_idx != amount_idx and
                                    not re.match(r'\d{2}\.\d{2}\.\d{4}', lines[desc_idx]) and
                                    ':' not in lines[desc_idx] and
                                    not re.search(r'[+-]?\d[\d\s]*,\d{2}', lines[desc_idx]) and
                                    len(lines[desc_idx]) > 5):
                                description = lines[desc_idx]
                                break

                        i = amount_idx + 1 if amount_str else i + 5

                    else:
                        # Нет времени, идем по другой структуре
                        trans_time = '00:00'
                        category = lines[i + 1] if i + 1 < len(lines) else ""

                        # Ищем сумму
                        amount_str = ""
                        for j in range(i + 2, min(i + 5, len(lines))):
                            if re.search(r'[+-]?\d[\d\s]*,\d{2}', lines[j]):
                                amount_str = lines[j]
                                break

                        description = ""
                        for j in range(i + 2, min(i + 6, len(lines))):
                            if (j != i + 2 or not amount_str) and not re.match(r'\d{2}\.\d{2}\.\d{4}', lines[j]):
                                description = lines[j]
                                break

                        i = i + 4 if amount_str else i + 3

                    # Обработка суммы
                    if amount_str:
                        amount_str_clean = unidecode(amount_str).replace(' ', '').replace(',', '.').replace('\xa0', '')

                        # Убираем знак + и определяем дебет/кредит
                        if amount_str_clean.startswith('+'):
                            amount_value = float(amount_str_clean[1:])
                            debit = 0
                            credit = amount_value
                        elif amount_str_clean.startswith('-'):
                            amount_value = float(amount_str_clean[1:])
                            debit = amount_value
                            credit = 0
                        else:
                            # Если нет знака, определяем по контексту
                            amount_value = float(amount_str_clean)
                            # Обычно положительные - пополнения, отрицательные - списания
                            debit = 0 if amount_value >= 0 else abs(amount_value)
                            credit = amount_value if amount_value >= 0 else 0

                        transaction = {
                            'bank': 'Sber',
                            'trans_datetime': datetime.strptime(f'{trans_date} {trans_time}', '%d.%m.%Y %H:%M'),
                            'transfer_datetime': datetime.strptime(trans_date, '%d.%m.%Y'),
                            'auth_code': '',
                            'category': category,
                            'debit': debit,
                            'credit': credit,
                            'text': description
                        }

                        transactions.append(transaction)

                else:
                    i += 1

    return transactions


if __name__ == '__main__':
    transactions = get_transactions()
    print(f"Found {len(transactions)} transactions")
    for t in transactions:
        print(f"{t['trans_datetime']} | {t['category']} | {t['text']} | Дебет: {t['debit']} | Кредит: {t['credit']}")