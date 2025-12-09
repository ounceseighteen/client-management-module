from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    company = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<Client {self.name}>'


def init_db():
    db.create_all()
    # Добавим тестовых клиентов, если база пустая
    if Client.query.count() == 0:
        test_clients = [
            Client(name='ООО "ТехноПрофи"', email='info@technoprofi.ru', phone='+79991234567', company='ТехноПрофи'),
            Client(name='ИП Иванов А.С.', email='ivanov@mail.ru', phone='+79998887766', company='ИП Иванов'),
            Client(name='Азимут Плюс', email='office@azimutplus.ru', phone='+78002005050', company='Азимут Плюс'),
        ]
        db.session.bulk_save_objects(test_clients)
        db.session.commit()