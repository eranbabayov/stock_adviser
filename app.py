from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mail import Mail
from app_configuration import app_configuration
import random
import string
from common_functions import *

app = Flask(__name__)
app = app_configuration(app)
mail = Mail(app)

failed_login_attempts = {}
blocked_ips = {}
ALL_SUPPORT_AVG = [20, 50, 150, 200]


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user_data = get_user_data_from_db(username=username)
        if user_data is None:
            flash('User does not exist')
            return redirect(url_for('login'))

        salt_bytes = bytes.fromhex(get_user_salt(user_id=user_data['user_id']))
        login_hashed_pwd = hashlib.pbkdf2_hmac(
            'sha256', password.encode('utf-8'), salt_bytes, 100000)
        user_hashed_password = bytes.fromhex(user_data['password'])

        if user_hashed_password == login_hashed_pwd:
            session['username'] = username
            session['user_id'] = user_data['user_id']
            failed_login_attempts[request.remote_addr] = 0
            stocks = get_stocks_based_to_user_id(session['user_id'])
            if stocks[0] is None:
                user_stocks = []
                watchlist_data = []
                stocks_close = {}
            else:
                user_stocks = stocks[0]
                stocks_close, watchlist_data = get_user_stocks_info(user_stocks)

            session['watchlist_data'] = watchlist_data
            session['stocks_close'] = stocks_close

            session['user_stocks'] = user_stocks  # Store the user's stocks in the session
            return render_template('dashboard.html', username=username, stocks=user_stocks, watchlist=watchlist_data)
        else:
            flash('Invalid username or password')
            failed_login_attempts[request.remote_addr] = failed_login_attempts.setdefault(request.remote_addr, 0) + 1
            return redirect(url_for('login'))

    return render_template(
        'login.html',
        user_added=request.args.get('user_added'), password_changed=request.args.get("password_changed"))


@app.route('/dashboard', methods=['POST'])
def dashboard():
    return render_template('dashboard.html', username=session['username'], stocks=session['user_stocks'],
                           watchlist=session['watchlist_data'])


@app.route('/stocks_above_avg', methods=['POST'])
def stocks_above_avg():
    avg_selection = request.form.getlist('avg_selection')
    if 'all_avg' in avg_selection:
        avg_selection = ALL_SUPPORT_AVG

    stocks_close, _ = get_user_stocks_info(session['user_stocks'], start_delta=365)
    stock_above_avg = check_which_stocks_above_avg(stocks=session['user_stocks'], stocks_close=stocks_close,
                                                   avg_selection=avg_selection)
    print(stock_above_avg)
    return render_template('dashboard.html', username=session['username'], stocks=session['user_stocks'],
                           watchlist=session['watchlist_data'], stock_above_avg=stock_above_avg)


@app.route('/add_stock', methods=['POST'])
def add_stock():
    stock_to_add = request.form.get('add_stock').upper()
    print(f"Form data: {request.form}")  # Debugging line
    user_stocks = session.get('user_stocks', [])  # Fetch the user's stocks from the session (or another source)
    if not stock_to_add or not check_if_etf_valid(stock_to_add):
        return render_template('dashboard.html', username=session['username'], stocks=user_stocks,
                               watchlist=session['watchlist_data'],
                               failed_msg="Please type a valid stock etf!!.")
    if stock_to_add in session['user_stocks']:
        return render_template('dashboard.html', username=session['username'], stocks=user_stocks,
                               watchlist=session['watchlist_data'],
                               failed_msg="The stock etf you entered already exists..")

    user_id = session['user_id']
    add_stocks_based_to_user_id(user_id=user_id, stock=stock_to_add)
    # Optionally update the stocks in session after adding
    user_stocks.append(stock_to_add)
    session['user_stocks'] = user_stocks
    print(f"stocks: {user_stocks}")
    stocks_close, watchlist_data = get_user_stocks_info([stock_to_add])

    session['watchlist_data'].append(watchlist_data[0])
    for stock_name, stock_val in stocks_close.items():
        session['stocks_close'][stock_name] = stock_val
    return render_template('dashboard.html', username=session['username'], stocks=user_stocks,
                           watchlist=session['watchlist_data']
                           , success_msg=rf"{stock_to_add} added successfully to your account!")


@app.route('/remove_stock', methods=['POST'])
def remove_stock():
    stock_to_remove = request.form.get('remove_stock').upper()
    user_stocks = session.get('user_stocks', [])
    if stock_to_remove not in session.get('user_stocks', user_stocks):
        return render_template('dashboard.html', username=session['username'], stocks=user_stocks,
                               watchlist=session['watchlist_data'],
                               failed_msg="The stock you requested to remove isnt in your stock list!")

    user_id = session['user_id']
    remove_stocks_based_to_user_id(user_id=user_id, stock=stock_to_remove)
    # Optionally update the stocks in session after adding
    user_stocks.remove(stock_to_remove)
    session['user_stocks'] = user_stocks
    print(f"stocks: {user_stocks}")
    session['watchlist_data'] = remove_stock_from_watchlist(session['watchlist_data'], stock_to_remove)
    del session['stocks_close'][stock_to_remove]
    return render_template('dashboard.html', username=session['username'], stocks=user_stocks,
                           watchlist=session['watchlist_data']
                           , success_msg=rf"{stock_to_remove} removed successfully from your account!")


@app.route("/password_reset_token", methods=["GET", "POST"])
def password_reset_token():
    if request.method == "POST":
        token = request.form.get("token")
        return redirect(url_for('password_change', token=token))
    return render_template('password_reset_token.html')


@app.route('/password_reset', methods=['GET', 'POST'])
def password_reset():
    if request.method == 'POST':
        user_email = request.form["email"]
        if check_if_user_exists_using_email(email=user_email):
            random_string = ''.join(
                random.choices(
                    string.ascii_uppercase +
                    string.digits,
                    k=20))
            hash_code = hashlib.sha1(
                random_string.encode('utf-8')).digest().hex()

            # Insert password reset info into the database
            insert_password_reset(user_email, hash_code)
            # Send email with the random string (randomly generated token)
            send_email(
                mail=mail,
                recipient=user_email,
                hash_code=random_string)

            flash('An email was sent check your mail inbox', 'info')
            return redirect(url_for('password_reset_token'))
        else:
            flash('The user does not exist', 'error')
            return redirect(url_for('password_reset'))
    else:
        return render_template('password_reset.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    _, salt_len = get_password_policy()
    if request.method == 'POST':
        new_username = request.form.get('username')
        new_password = request.form.get('password')
        new_email = request.form.get('email')
        if check_if_user_exists_using_email(new_email):
            flash("Email already exists! please use different email or login to your account.")
            return redirect(url_for('register'))
        if not validate_password(new_password):
            return redirect(url_for('register'))

        user_data = get_user_data_from_db(username=new_username)
        if user_data:
            flash('Username already exists')
            return redirect(url_for('register'))
        new_password_hashed_hex, user_salt_hex = generate_new_password_hashed(new_password, generate_to_hex=True)
        insert_new_user_to_db(
            new_username,
            new_password_hashed_hex,
            new_email,
            user_salt_hex)
        user_id = get_user_data_from_db(username=new_username)['user_id']
        session['username'] = new_username
        session['user_id'] = user_id
        return redirect(url_for('login', user_added="user added"))

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/set_new_pwd', methods=['GET', 'POST'])
def set_new_pwd():
    user_data = session.get('user_data')
    username = session.get("username")
    if not user_data and not username:
        return redirect(url_for('index'))
    if request.method == "POST":
        if not user_data:
            user_data = get_user_data_from_db(username=username)
        if user_data:
            user_email = user_data["email"]
            new_password = request.form.get('new_pwd')
            old_password = request.form.get('old_pwd')

            if (isinstance(old_password, str)):
                if not compare_to_current_password(user_data, old_password):
                    flash("The old password you inserted does not match the current used password.\nPlease try again")
                    return redirect(url_for('set_new_pwd', _method='GET'))

                if not validate_password(new_password):
                    return redirect(url_for('set_new_pwd', _method='GET'))

                if change_user_password_in_db(user_email, new_password):
                    return redirect(url_for('/', password_changed=True))

            else:  # reset from email
                if not validate_password(new_password):
                    return redirect(url_for('set_new_pwd', emailReset=True))
                if change_user_password_in_db(user_email, new_password):
                    return redirect(url_for('/', password_changed=True))
                return redirect(url_for('set_new_pwd', emailReset=True))

    return render_template('set_new_pwd.html', emailReset=request.args.get('emailReset'))


@app.route('/stock/<symbol>', methods=['GET'])
def get_stock_data(symbol):
    stocks_close, _ = get_user_stocks_info([symbol], start_delta=365)
    day_20_avg = get_stocks_moving_avg([symbol], stocks_close, moving_avg=20)
    day_50_avg = get_stocks_moving_avg([symbol], stocks_close, moving_avg=50)
    day_150_avg = get_stocks_moving_avg([symbol], stocks_close, moving_avg=150)
    day_200_avg = get_stocks_moving_avg([symbol], stocks_close, moving_avg=200)
    return jsonify({
        "stocks_close": stocks_close,
        "day_20_avg": day_20_avg,
        "day_50_avg": day_50_avg,
        "day_150_avg": day_150_avg,
        "day_200_avg": day_200_avg
    })


@app.route('/live_stocks', methods=['GET'])
def live_stocks():
    # Example list of stocks to update
    user_stocks = session.get('user_stocks', [])
    stock_data = get_last_day_stock_data(user_stocks)
    return jsonify(stock_data)


@app.route('/user_trades', methods=['GET'])
def user_trades():
    # Example list of stocks to update
    user_trades = get_user_trades(session["user_id"])
    return render_template('trades.html', user_trades=user_trades)\



@app.route('/add_trade', methods=['POST'])
def add_trade():
    stock_etf = request.form['stock_etf']
    buy_price = float(request.form['buy_price'])
    buy_date = datetime.strptime(request.form['buy_date'], '%Y-%m-%d')
    sell_price = float(request.form['sell_price']) if request.form['sell_price'] else None
    sell_date = datetime.strptime(request.form['sell_date'], '%Y-%m-%d') if request.form['sell_date'] else None

    # Add trade to database (replace with your actual DB code)
    add_new_trade(user_id=session["user_id"], stock_etf=stock_etf, buy_price=buy_price, buy_date=buy_date,
                  sell_date=sell_date, sell_price=sell_price)

    return redirect(url_for('user_trades'))  # Redirect to the trades page after adding a new trade


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
