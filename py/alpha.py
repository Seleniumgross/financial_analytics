import glob
from datetime import datetime
import pandas as pd

PATH = '../input/alpha'


def get_alpha_transactions():
    filenames = glob.glob(PATH + '/*.CSV')
    transactions = []

    for filename in filenames:
        df = pd.read_csv(filename, encoding='utf-8-sig', sep=',', parse_dates=['operationDate', 'transactionDate'])

        for _, row in df.iterrows():
            amount = float(str(row['amount']).replace(' ', ''))

            if row['type'] == 'Списание':
                debit = 0
                credit = abs(amount)
            else:
                debit = amount
                credit = 0

            trans_datetime = row['operationDate']
            transfer_datetime = row['transactionDate']

            if isinstance(trans_datetime, datetime) and trans_datetime.time() == pd.Timestamp('00:00:00').time():
                trans_datetime = trans_datetime.replace(hour=12, minute=0, second=0)

            # ИСПРАВЛЕНИЕ: безопасное преобразование в строку
            merchant = str(row.get('merchant', ''))
            comment = str(row.get('comment', '')) if pd.notna(row.get('comment')) else ''
            text = f"{merchant} - {comment}".strip(' -')

            transaction = {
                'bank': 'Alpha',
                'trans_datetime': trans_datetime,
                'transfer_datetime': transfer_datetime,
                'pan': str(row.get('cardNumber', '')),
                'status': row['status'],
                'debit': debit,
                'credit': credit,
                'trans_currency': row['currency'],
                'pay_sum': amount,
                'pay_currency': row['currency'],
                'cashback': '',
                'category': row['category'],
                'mcc': str(row.get('mcc', '')).replace('.0', '') if pd.notna(row.get('mcc')) else '',
                'text': text,
                'bonus': float(row.get('bonusValue', 0)) if pd.notna(row.get('bonusValue')) else 0.0,
                'rounding': 0.0,
                'sum_with_rounding': amount
            }

            transactions.append(transaction)

    return transactions