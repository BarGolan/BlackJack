from aifc import Error
from flask import *
import sqlite3
import random

app = Flask(__name__)

cards = []
player_hand = []
dealer_hand = []


def create_connection():
    conn = None
    try:
        conn = sqlite3.connect('gambler.db')
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred while creating connection")
    return conn


@app.route('/', methods=['GET', 'POST'])
def index():
    # Creates the db if is not already exists
    conn = create_connection()
    c = conn.cursor()
    c.execute(
        'CREATE TABLE IF NOT EXISTS games (game INTEGER, op_id INTEGER, op text, time DATETIME, player_hand text, dealer_hand text, player_win INTEGERs);')

    count = 0
    conn.commit()
    conn.close()

    return render_template('index.html', count=count)


@app.route('/new_game', methods=['GET', 'POST'])
def new_game():
    global player_hand, dealer_hand

    create_new_deck()

    player_hand = []
    dealer_hand = []
    deal()

    tuple_of_lists = (player_hand, dealer_hand)
    return json.dumps(tuple_of_lists)


def create_new_deck():
    global cards
    suits = ['♥️', '♠️', '♣️', '♦️']
    num_strings = list(map(str, range(2, 11)))
    royals = ['J', 'Q', 'K', 'A']
    cards = cards + [n + s for s in suits for n in num_strings + royals]


def deal():
    global dealer_hand
    global player_hand
    draw_from_deck = []
    for i in range(0, 4):
        random_card = random.randint(0, len(cards) - 1)
        draw_from_deck.append(cards.pop(random_card))

    dealer_hand.append(draw_from_deck[0])
    dealer_hand.append(draw_from_deck[1])
    player_hand.append(draw_from_deck[2])
    player_hand.append(draw_from_deck[3])

    print(f'Player: {player_hand}   sum is {sum(player_hand)}')
    print(f'Dealer: {dealer_hand}   sum is {sum(dealer_hand)}')


@app.route('/dealPlayer')
def dealPlayer():
    random_card = random.randint(0, len(cards) - 1)
    player_hand.append(cards.pop(random_card))
    print(f'Player: {player_hand}   sum is {sum(player_hand)}')
    return json.dumps(player_hand)


@app.route('/is_bust')
def is_bust():
    if all(sum > 21 for sum in sum(player_hand)):
        print('Bust! You Lost')
        return json.dumps('Bust')
    return json.dumps('No bust')


@app.route('/dealDealer')
def dealDealer():
    random_card = random.randint(0, len(cards) - 1)
    dealer_hand.append(cards.pop(random_card))
    print(f'Dealer: {dealer_hand}   sum is {sum(dealer_hand)}')
    tuple = (dealer_hand, sum(dealer_hand)[0])
    return json.dumps(tuple)


@app.route('/winner')
def winner():
    dealer_max = max_under_21(dealer_hand)
    player_max = max_under_21(player_hand)
    if dealer_max > player_max:
        message = 'You Lost! Dealer has a better hand'
        print(message)
        return json.dumps(message)
    elif dealer_max < player_max:
        message = 'You Won! You have a better hand'
        print(message)
        return json.dumps(message)
    else:
        message = 'Split! you and the dealer have equal hands'
        print(message)
        return json.dumps(message)


def max_under_21(hand):
    maximum = max(sum(hand))
    if maximum > 21:
        return min(sum(hand))
    return maximum


def sum(hand):
    sum1 = 0
    sum2 = 0
    for card in hand:
        c = card[:-2]
        if c in ['J', 'Q', 'K', 'A']:
            if c == 'A':
                sum1 += 1
                sum2 += 11
            else:
                sum1 += 10
                sum2 += 10
        else:
            sum1 += int(c)
            sum2 += int(c)
    return (sum1, sum2)


@app.route('/init_dealer_sum')
def init_dealer_sum():
    sum1 = 0
    for card in dealer_hand:
        c = card[:-2]
        if c in ['J', 'Q', 'K', 'A']:
            if c == 'A':
                sum1 += 1
            else:
                sum1 += 10
        else:
            sum1 += int(c)
    return json.dumps(sum1)


def insert_to_db():
    return


@app.route('/increment_click', methods=['POST'])
def increment_click():

    # Increment the click count in the database
    conn = create_connection()
    c = conn.cursor()
    button_id = request.form['button_id']
    c.execute('SELECT count FROM games WHERE ID=(?);', (button_id))

    row = c.fetchone()
    last_count = 0
    if row is not None:
        last_count = row[0]
    else:
        last_count = 0

    new_count = last_count + 1 if last_count else 1
    c.execute('UPDATE games SET count=(?) WHERE ID=(?);',
              (new_count, button_id))
    conn.commit()
    conn.close()
    return jsonify(new_count)


@app.route('/get_click_count', methods=['GET'])
def get_click_count():
    # Get the current click count from the database
    conn = create_connection()
    c = conn.cursor()
    button_id = request.args.get('button_id')
    c.execute('SELECT count FROM games WHERE ID=(?);', (button_id))
    row = c.fetchone()
    click_count = 0
    if row is not None:
        click_count = row[0]
    else:
        click_count = 0
    conn.close()
    return jsonify(click_count)


if __name__ == '__main__':
    app.run(debug=True)
