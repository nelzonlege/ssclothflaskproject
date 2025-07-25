from flask import Flask, render_template, request, redirect, url_for, session

import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="ss_cloth_db"
)
cursor = db.cursor()
app.secret_key = 'your_secret_key_here' 


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/shop')
def index():
    query = request.args.get('q', '')
    if query:
        cursor.execute("SELECT * FROM clothes WHERE name LIKE %s", ('%' + query + '%',))
    else:
        cursor.execute("SELECT * FROM clothes")
    clothes = cursor.fetchall()

    cart = session.get('cart', [])
    return render_template('index.html', clothes=clothes, query=query, cart=cart)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        category = request.form['category']
        stock = request.form['stock']
        cursor.execute("INSERT INTO clothes (name, price, category, stock) VALUES (%s, %s, %s, %s)",
                       (name, price, category, stock))
        db.commit()
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        category = request.form['category']
        stock = request.form['stock']
        cursor.execute("UPDATE clothes SET name=%s, price=%s, category=%s, stock=%s WHERE id=%s",
                       (name, price, category, stock, id))
        db.commit()
        return redirect(url_for('index'))

    cursor.execute("SELECT * FROM clothes WHERE id = %s", (id,))
    cloth = cursor.fetchone()
    return render_template('edit.html', cloth=cloth)


@app.route('/delete/<int:id>')
def delete(id):
    cursor.execute("DELETE FROM clothes WHERE id = %s", (id,))
    db.commit()
    return redirect(url_for('index'))


@app.route('/add_to_cart/<int:id>')
def add_to_cart(id):
    cart = session.get('cart', [])
    if id not in cart:
        cart.append(id)
    session['cart'] = cart
    return redirect(url_for('index'))


@app.route('/cart')
def view_cart():
    cart = session.get('cart', [])
    items = []
    if cart:
        format_strings = ','.join(['%s'] * len(cart))
        cursor.execute(f"SELECT * FROM clothes WHERE id IN ({format_strings})", tuple(cart))
        items = cursor.fetchall()
    return render_template('cart.html', items=items)

@app.route('/remove_from_cart/<int:id>')
def remove_from_cart(id):
    cart = session.get('cart', [])
    if id in cart:
        cart.remove(id)
    session['cart'] = cart
    return redirect(url_for('view_cart'))


@app.route('/clear_cart')
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('view_cart'))


if __name__ == '__main__':
    app.run(debug=True)
