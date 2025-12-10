from flask import Flask, render_template, request, jsonify, send_file
from database import db, init_db, Client
import io
import csv
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clients.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация базы данных
db.init_app(app)


# Главная страница
@app.route('/')
def index():
    return render_template('index.html')


# Получить всех клиентов (API)
@app.route('/api/clients', methods=['GET'])
def get_clients():
    clients = Client.query.all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'email': c.email,
        'phone': c.phone,
        'company': c.company,
        'created_at': c.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for c in clients])


# Добавить клиента (API)
@app.route('/api/clients', methods=['POST'])
def add_client():
    data = request.json
    new_client = Client(
        name=data.get('name'),
        email=data.get('email'),
        phone=data.get('phone'),
        company=data.get('company', '')
    )
    db.session.add(new_client)
    db.session.commit()
    return jsonify({'message': 'Клиент добавлен', 'id': new_client.id}), 201


# Удалить клиента (API)
@app.route('/api/clients/<int:client_id>', methods=['DELETE'])
def delete_client(client_id):
    client = Client.query.get_or_404(client_id)
    db.session.delete(client)
    db.session.commit()
    return jsonify({'message': 'Клиент удален'})


# Веб-интерфейс для просмотра клиентов
@app.route('/clients')
def clients_page():
    clients = Client.query.all()
    return render_template('clients.html', clients=clients)


# Экспорт в HTML (работает в любом браузере)
@app.route('/export/html')
def export_html():
    clients = Client.query.all()

    # Создаем HTML документ
    html_content = '''
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Список клиентов - Азимут Плюс</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 40px;
                line-height: 1.6;
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
                border-bottom: 2px solid #4f46e5;
                padding-bottom: 20px;
            }
            h1 {
                color: #4f46e5;
                font-size: 28px;
                margin-bottom: 10px;
            }
            .subtitle {
                color: #666;
                font-size: 16px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            th {
                background-color: #4f46e5;
                color: white;
                padding: 12px;
                text-align: left;
                font-weight: 600;
            }
            td {
                padding: 10px;
                border-bottom: 1px solid #ddd;
            }
            tr:hover {
                background-color: #f5f5f5;
            }
            .footer {
                margin-top: 40px;
                text-align: center;
                color: #666;
                font-size: 14px;
                border-top: 1px solid #ddd;
                padding-top: 20px;
            }
            .info {
                background-color: #f8fafc;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>СПИСОК КЛИЕНТОВ</h1>
            <div class="subtitle">Азимут Плюс | Производственная практика 2025</div>
            <div class="subtitle">Дата экспорта: ''' + datetime.now().strftime('%d.%m.%Y %H:%M') + '''</div>
        </div>
    '''

    if clients:
        html_content += '''
        <div class="info">
            <strong>Всего клиентов:</strong> ''' + str(len(clients)) + '''
        </div>

        <table>
            <thead>
                <tr>
                    <th>№</th>
                    <th>Имя клиента</th>
                    <th>Email</th>
                    <th>Телефон</th>
                    <th>Компания</th>
                </tr>
            </thead>
            <tbody>
        '''

        for i, client in enumerate(clients, 1):
            html_content += f'''
                <tr>
                    <td>{i}</td>
                    <td>{client.name or ''}</td>
                    <td>{client.email or ''}</td>
                    <td>{client.phone or '-'}</td>
                    <td>{client.company or '-'}</td>
                </tr>
            '''

        html_content += '''
            </tbody>
        </table>
        '''
    else:
        html_content += '''
        <div style="text-align: center; padding: 40px;">
            <p style="font-size: 18px; color: #666;">Нет данных о клиентах</p>
        </div>
        '''

    html_content += '''
        <div class="footer">
            <p>Азимут Плюс © 2025</p>
            <p>Разработано в рамках производственной практики</p>
            <p>Для печати: нажмите Ctrl+P или выберите "Печать" в меню браузера</p>
        </div>
    </body>
    </html>
    '''

    # Возвращаем HTML файл
    buffer = io.BytesIO(html_content.encode('utf-8'))

    return send_file(
        buffer,
        as_attachment=True,
        download_name='clients_export.html',
        mimetype='text/html'
    )


# Экспорт в CSV
@app.route('/export/csv')
def export_csv():
    clients = Client.query.all()

    buffer = io.StringIO()
    writer = csv.writer(buffer)

    # Заголовки
    writer.writerow(['ID', 'Имя', 'Email', 'Телефон', 'Компания', 'Дата создания'])

    for client in clients:
        writer.writerow([
            client.id,
            client.name,
            client.email,
            client.phone or '',
            client.company or '',
            client.created_at.strftime('%d.%m.%Y %H:%M')
        ])

    buffer.seek(0)

    return send_file(
        io.BytesIO(buffer.getvalue().encode('utf-8-sig')),
        as_attachment=True,
        download_name='clients_export.csv',
        mimetype='text/csv'
    )


if __name__ == '__main__':
    with app.app_context():
        init_db()
    print("Сервер запущен: http://localhost:5000")
    app.run(debug=True, port=5000)