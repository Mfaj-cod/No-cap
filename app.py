from flask import Flask, render_template, request, redirect, session, url_for, flash
import os, sqlite3, razorpay, smtplib
from email.mime.text import MIMEText
from random import random
from init_db import init_db, insert_products, insert_categories
from data import PRODUCTS, CATEGORIES
import json


DB_NAME = 'store.db'
init_db()
insert_products(PRODUCTS)
insert_categories(CATEGORIES)


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'devsecret')


# for email sending
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USER = os.environ.get('SMTP_USER')  
SMTP_PASS = os.environ.get('SMTP_PASS')  
OWNER_EMAIL = os.environ.get('OWNER_EMAIL')


# Razorpay client from env
RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET')
client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


# Database helpers
def get_products():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT id,name,description,price,image_url,category,ingredients,reviews FROM products')
    products = []
    for row in c.fetchall():
        products.append({
            'id': row[0],
            'name': row[1],
            'description': row[2],
            'price': row[3],
            'image_url': row[4],
            'category': row[5],
            'ingredients': json.loads(row[6]) if row[6] else [],
            'reviews': json.loads(row[7]) if row[7] else []
        })
    conn.close()
    return products


def get_product(pid):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT id,name,description,price,image_url,category,ingredients,reviews FROM products WHERE id=?', (pid,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    return {
        'id': row[0],
        'name': row[1],
        'description': row[2],
        'price': row[3],
        'image_url': row[4],
        'category': row[5],
        'ingredients': json.loads(row[6]) if row[6] else [],
        'reviews': json.loads(row[7]) if row[7] else []
    }


def get_categories():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT name,image_url FROM categories')
    cats = [{'name': row[0], 'image_url': row[1]} for row in c.fetchall()]
    conn.close()
    return cats



# Routes
@app.route('/')
def index():
    return render_template('index.html', featured_products=get_products()[:4], categories=get_categories(), random=random)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        message = request.form['message']

        # Construct the email body
        body = f"""
        You have received a new message from your Kerala Spices website contact form:

        Name: {name}
        Email: {email}
        Phone: {phone}

        Message:
        {message}
        """

        try:
            msg = MIMEText(body)
            msg['Subject'] = f"New Customer Query from {name}"
            msg['From'] = SMTP_USER
            msg['To'] = OWNER_EMAIL

            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
            server.quit()
            flash('Your message has been sent successfully! We will contact you soon.', 'success')
        except Exception as e:
            print("SMTP Error:", e)
            flash('Failed to send message. Please try again later.', 'danger')

        return redirect(url_for('contact'))

    return render_template('contact.html')



@app.route('/category/<string:category_name>')
def category(category_name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT id,name,description,price,image_url,category,ingredients,reviews FROM products WHERE category=?', (category_name,))
    products = [dict(id=row[0], name=row[1], description=row[2], price=row[3],
                     image_url=row[4], category=row[5], ingredients=json.loads(row[6]), reviews=json.loads(row[7])) 
                for row in c.fetchall()]
    conn.close()
    return render_template('category.html', category_name=category_name, products=products)


@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('email')
    if not email:
        flash('Please enter a valid email', 'warning')
        return redirect(url_for('index'))
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO subscriptions (email) VALUES (?)', (email,))
        conn.commit()
        flash('Subscribed successfully!', 'success')
    except sqlite3.IntegrityError:
        flash('Email already subscribed.', 'info')
    conn.close()
    return redirect(url_for('index'))



@app.route('/product/<int:pid>')
def product(pid):
    p = get_product(pid)
    if not p: 
        return "Product not found", 404
    # Related products (same category)
    all_products = get_products()
    related = [prod for prod in all_products if prod['category']==p['category'] and prod['id']!=p['id']]
    return render_template('product.html', product=p, related_products=related[:4])


@app.route('/cart')
def cart():
    cart = session.get('cart', {})
    items = []
    total = 0
    for pid, qty in cart.items():
        p = get_product(int(pid))
        if p:
            subtotal = p['price']*qty
            total += subtotal
            items.append({'product': p, 'quantity': qty, 'subtotal': subtotal})
    print(items)
    return render_template('cart.html', cart_items=items, cart_total=total)


@app.route('/add_to_cart/<int:pid>', methods=['POST'])
def add_to_cart(pid):
    qty = int(request.form.get('quantity',1))
    cart = session.get('cart', {})
    cart[str(pid)] = cart.get(str(pid),0)+qty
    session['cart'] = cart
    flash('Added to cart','success')
    return redirect(url_for('cart'))


@app.route('/update_cart/<int:pid>', methods=['POST'])
def update_cart(pid):
    qty = int(request.form.get('quantity', 1))
    cart = session.get('cart', {})
    if qty > 0:
        cart[str(pid)] = qty
    else:
        cart.pop(str(pid), None)
    session['cart'] = cart
    flash('Cart updated successfully!', 'success')
    return redirect(url_for('cart'))


@app.route('/remove_from_cart/<int:pid>', methods=['POST'])
def remove_from_cart(pid):
    cart = session.get('cart', {})
    cart.pop(str(pid), None)
    session['cart'] = cart
    flash('Item removed from cart.', 'success')
    return redirect(url_for('cart'))



@app.route('/checkout', methods=['GET','POST'])
def checkout():
    cart = session.get('cart', {})
    if not cart:
        flash('Cart empty','warning')
        return redirect(url_for('index'))

    items = []
    total = 0
    for pid, qty in cart.items():
        p = get_product(int(pid))
        if p:
            subtotal = p['price']*qty
            total += subtotal
            items.append({'product': p, 'quantity': qty, 'subtotal': subtotal})

    razor_order = None
    order_id = None
    key_id = None

    if request.method=='POST':
        data = request.form
        name = data['name']
        email = data['email']
        phone = data['phone']
        address = data['address']
        city = data['city']
        state = data['state']
        pincode = data['pincode']
        payment_method = data['payment_method']

        # Save order
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('''INSERT INTO orders 
                     (name,email,phone,address,city,state,pincode,payment_method,total,status) 
                     VALUES (?,?,?,?,?,?,?,?,?,?)''',
                  (name,email,phone,address,city,state,pincode,payment_method,total,'pending'))
        order_id = c.lastrowid
        for it in items:
            c.execute('''INSERT INTO order_items 
                         (order_id,product_id,quantity,price) 
                         VALUES (?,?,?,?)''',
                      (order_id,it['product']['id'],it['quantity'],it['product']['price']))
        conn.commit()
        conn.close()

        # Razorpay order
        if RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET:
            razor_order = client.order.create({'amount':int(total*100),'currency':'INR','receipt':str(order_id)})
            key_id = RAZORPAY_KEY_ID

    return render_template('checkout.html', cart_items=items, cart_total=total,
                           razor_order=razor_order, order_id=order_id, key_id=key_id)



@app.route('/success', methods=['POST'])
def success():
    order_id = request.form.get('order_id')
    payment_id = request.form.get('razorpay_payment_id')

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('UPDATE orders SET status=? WHERE id=?',('paid',order_id))
    conn.commit()
    conn.close()

    flash(f'Payment successful! Payment ID: {payment_id}','success')
    session['cart'] = {}
    # Optional: Fetch order details for success page
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM orders WHERE id=?',(order_id,))
    row = c.fetchone()
    conn.close()
    order = None
    if row:
        order = {
            'id': row[0], 'name': row[1], 'email': row[2],
            'phone': row[3], 'address': row[4], 'city': row[5],
            'state': row[6], 'pincode': row[7],
            'payment_method': row[8], 'total': row[9], 'status': row[10]
        }

    return render_template('success.html', order=order, payment_id=payment_id)

@app.route('/failure', methods=['GET'])
def failure():
    flash('Payment failed or cancelled','danger')
    return render_template('failure.html')


if __name__=='__main__':
    app.run(debug=True)
