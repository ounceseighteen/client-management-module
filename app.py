from flask import Flask, render_template, request, jsonify, send_file
from database import db, init_db, Client
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import csv

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


# Экспорт в PDF (ваше задание от 15.12.25)
@app.route('/export/pdf')
def export_pdf():
    clients = Client.query.all()

    # Создаем PDF в памяти
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, "Список клиентов")
    p.setFont("Helvetica", 12)

    y = 750
    for i, client in enumerate(clients, 1):
        text = f"{i}. {client.name} - {client.email} - {client.phone}"
        p.drawString(50, y, text)
        y -= 20
        if y < 50:  # Если место заканчивается, новая страница
            p.showPage()
            p.setFont("Helvetica", 12)
            y = 750

    p.save()
    buffer.seek(0)

    return send_file(buffer,
                     as_attachment=True,
                     download_name='clients_export.pdf',
                     mimetype='application/pdf')


# Экспорт в CSV
@app.route('/export/csv')
def export_csv():
    clients = Client.query.all()

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(['ID', 'Имя', 'Email', 'Телефон', 'Компания', 'Дата создания'])

    for client in clients:
        writer.writerow([
            client.id,
            client.name,
            client.email,
            client.phone,
            client.company,
            client.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])

    buffer.seek(0)

    return send_file(
        io.BytesIO(buffer.getvalue().encode('utf-8')),
        as_attachment=True,
        download_name='clients_export.csv',
        mimetype='text/csv'
    )


if __name__ == '__main__':
    with app.app_context():
        init_db()
    print("Сервер запущен: http://localhost:5000")
    print("Swagger UI: http://localhost:5000/apidocs")
    app.run(debug=True, port=5000)