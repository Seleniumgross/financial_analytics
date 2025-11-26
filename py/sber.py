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
            lines = text.split('\n')

            i = 0
            while i < len(lines) - 3:
                # Ищем дату операции в формате 10.11.2025
                if re.match(r'\d{2}\.\d{2}\.\d{4}', lines[i]):
                    trans_date = lines[i]

                    # Проверяем есть ли время на следующей строке
                    if i + 1 < len(lines) and ':' in lines[i + 1]:
                        trans_time = lines[i + 1]
                        category = lines[i + 2] if i + 2 < len(lines) else ""
                        amount_str = lines[i + 3] if i + 3 < len(lines) else ""

                        # Пропускаем строку с датой обработки и кодом
                        if i + 4 < len(lines) and re.match(r'\d{2}\.\d{2}\.\d{4}', lines[i + 4]):
                            description = lines[i + 5] if i + 5 < len(lines) else ""
                            i += 6
                        else:
                            description = ""
                            i += 4
                    else:
                        # Если нет времени, ищем категорию и сумму
                        trans_time = '00:00'
                        category = lines[i + 1] if i + 1 < len(lines) else ""
                        amount_str = lines[i + 2] if i + 2 < len(lines) else ""
                        description = lines[i + 3] if i + 3 < len(lines) else ""
                        i += 4

                    # Пропускаем если это не сумма
                    if re.match(r'\d{2}\.\d{2}\.\d{4}', amount_str) or not amount_str.strip():
                        continue

                    # Обработка суммы
                    amount_str_clean = unidecode(amount_str).replace(' ', '').replace(',', '.')

                    try:
                        if amount_str_clean.startswith('+'):
                            amount = float(amount_str_clean[1:])
                            debit = 0
                            credit = amount
                        else:
                            amount = float(amount_str_clean)
                            debit = amount
                            credit = 0

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

                    except (ValueError, IndexError):
                        i += 1
                        continue
                else:
                    i += 1

    return transactions


if __name__ == '__main__':
    transactions = get_transactions()
    print(f"Found {len(transactions)} transactions")
    for t in transactions[:3]:  # покажем первые 3
        print(t)