import json
import sqlalchemy
from sqlalchemy import VARCHAR, Integer, TIMESTAMP, CHAR, insert, delete, update, select, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from connect_MySQL import engine

# テーブル(model)の定義
class Base(DeclarativeBase):
    pass

class Products(Base):
    __tablename__ = 'product'
    PRD_ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    CODE: Mapped[str] = mapped_column(VARCHAR(13), unique=True, nullable=False)
    NAME: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    PRICE: Mapped[int] = mapped_column(Integer, nullable=False)

class Trade(Base):
    __tablename__ = 'trade'
    TRD_ID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    DATETIME: Mapped[str] = mapped_column(TIMESTAMP)
    EMP_CD: Mapped[str] = mapped_column(CHAR(10), nullable=False)
    STORE_CD: Mapped[str] = mapped_column(CHAR(5), nullable=False)
    POS_NO: Mapped[str] = mapped_column(CHAR(3), nullable=False)
    TOTAL_AMT: Mapped[int] = mapped_column(Integer, default=0)
    TTL_AMT_EX_TAX: Mapped[int] = mapped_column(Integer, default=0)

class Detail(Base):
    __tablename__ = 'detail'
    TRD_ID: Mapped[int] = mapped_column(Integer, ForeignKey('trade.TRD_ID'), primary_key=True, nullable=False)
    DTL_ID: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    PRD_ID: Mapped[int] = mapped_column(Integer, nullable=False)
    PRD_CODE: Mapped[str] = mapped_column(CHAR(13), nullable=False)
    PRD_NAME: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    PRD_PRICE: Mapped[int] = mapped_column(Integer, nullable=False)
    TAX_CD: Mapped[str] = mapped_column(CHAR(2), nullable=False)

def myselect(mytable, code):
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        with session.begin():
            result = session.query(mytable).filter(mytable.CODE == code).first()
        
        if result is None:
            session.close()
            return None
            # return json.dumps({'error': '該当する商品が存在しません。'})
        result_dict = {
            'product_id': result.PRD_ID,
            'code': result.CODE,
            'name': result.NAME,
            'price': result.PRICE
        }
        # result_json = json.dumps(result_dict, ensure_ascii=False)
    except sqlalchemy.exc.IntegrityError:
        print("一意制約違反により、挿入に失敗しました")

    session.close()
    return result_dict

def insert_trade(mytable, values):
    Session = sessionmaker(bind=engine)
    session = Session()

    query = insert(mytable).values(values)

    try:
        with session.begin():
            result = session.execute(query)
            trade_id = result.lastrowid # auto incrementの値を取得
    except sqlalchemy.exc.IntegrityError:
        print("一意制約違反により、挿入に失敗しました")
    
    session.close()
    return trade_id

def insert_item(mytable, values):
    Session = sessionmaker(bind=engine)
    session = Session()

    query = insert(mytable).values(values)

    try:
        with session.begin():
            result = session.execute(query)
    except sqlalchemy.exc.IntegrityError:
        print("一意制約違反により、挿入に失敗しました")
    
    session.close()
    return 'item inserted'

def update_trade(mytable, values):
    Session = sessionmaker(bind=engine)
    session = Session()

    trade_id = values.pop('TRD_ID')
    query = update(mytable).where(mytable.TRD_ID == trade_id).values(values)

    try:
        with session.begin():
            result = session.execute(query)
    except sqlalchemy.exc.IntegrityError:
        print("一意制約違反により、挿入に失敗しました")
        session.rollback() # データ更新に失敗したら、前の状態に戻す
    
    session.close()
    return 'trade updated'