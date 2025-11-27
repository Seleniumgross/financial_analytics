import logging

import sber

import tinkoff
import vtb
import alpha
from connect import session, SberTransaction, TinkoffTransaction, VTBTransaction, AlphaTransaction

from sqlalchemy.dialects.postgresql import insert

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s - %(filename)s:%(lineno)s:%(funcName)s()',
)

logger = logging.getLogger(__name__)


transactions = {
    'sber': (sber.get_transactions(), SberTransaction),
    'tinkoff': (tinkoff.get_transactions(), TinkoffTransaction),
    'vtb': (vtb.get_transactions(), VTBTransaction),
    'alpha': (alpha.get_alpha_transactions(), AlphaTransaction)
}

for _, (source_transactions, TransactionClass) in transactions.items():
    for transaction in source_transactions:
        logger.debug(transaction)
        session.execute(insert(TransactionClass).values(transaction).on_conflict_do_nothing())
        session.commit()

session.close()
