from aifc import Error
from flask import *
import sqlite3
import random
import datetime


app = Flask(__name__)

cards = []
player_hand = []
dealer_hand = []
game = 0
op_id = 0
wins = ties = losses = hit_me_win_rate = stand_win_rate = 0


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
        'CREATE TABLE IF NOT EXISTS games (game INTEGER, op_id INTEGER, op text, time DATETIME, player_hand text, dealer_hand text, player_win INTEGER);')

    c.execute(
        'CREATE TABLE IF NOT EXISTS current_game (game INTEGER, op_id INTEGER, op text, time DATETIME, player_hand text, dealer_hand text, player_win INTEGER);')
    count = 0
    conn.commit()
    conn.close()

    return render_template('index.html', count=count)


@app.route('/new_game', methods=['GET', 'POST'])
def new_game():
    global player_hand, dealer_hand, game, op_id
    create_new_deck()
    player_hand = []
    dealer_hand = []

    deal()
    # deal_test()
    tuple_of_lists = (player_hand, dealer_hand)

    conn = create_connection()
    c = conn.cursor()
    # delete content of current-game table
    c.execute('DELETE FROM current_game;')
    # gets the last game in he 'games' table from gambler db.
    c.execute('SELECT MAX(game) FROM games;')
    # Fetch the result
    result = c.fetchone()
    if result[0] is None:
        game = 1
    else:
        game = result[0] + 1
    op_id = 0

    # commit the changes and close the connection
    conn.commit()
    conn.close()
    insert_new_row_to_current()

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


def deal_test():
    global dealer_hand
    global player_hand
    draw_from_deck = []

    card_index = cards.index('10♥️')
    draw_from_deck.append(cards.pop(card_index))
    card_index = cards.index('A♣️')
    draw_from_deck.append(cards.pop(card_index))
    card_index = cards.index('8♣️')
    draw_from_deck.append(cards.pop(card_index))
    card_index = cards.index('5♥️')
    draw_from_deck.append(cards.pop(card_index))

    dealer_hand.append(draw_from_deck[0])
    dealer_hand.append(draw_from_deck[1])
    player_hand.append(draw_from_deck[2])
    player_hand.append(draw_from_deck[3])

    print(f'Player: {player_hand}   sum is {sum(player_hand)}')
    print(f'Dealer: {dealer_hand}   sum is {sum(dealer_hand)}')


@app.route('/dealPlayer')
def dealPlayer():
    global op_id, wins
    random_card = random.randint(0, len(cards) - 1)
    player_hand.append(cards.pop(random_card))
    print(f'Player: {player_hand}   sum is {sum(player_hand)}')

    if op_id != 0:
        insert_new_row_to_current()
    insert_to_current('player_hand', ''.join(player_hand[:-1]))
    insert_to_current('dealer_hand', dealer_hand[0])
    insert_to_current('op', 'hit me')
    current_time = datetime.datetime.now()
    insert_to_current('time', current_time)
    op_id += 1

    return json.dumps(player_hand)


@app.route('/is_bust')
def is_bust():
    if all(sum > 21 for sum in sum(player_hand)):
        print('Bust! You Lost')
        return json.dumps('Bust')
    return json.dumps('No bust')


@app.route('/dealDealer')
def dealDealer():
    global op_id
    random_card = random.randint(0, len(cards) - 1)
    dealer_hand.append(cards.pop(random_card))
    print(f'Dealer: {dealer_hand}   sum is {sum(dealer_hand)}')
    tuple = (dealer_hand, sum(dealer_hand)[0])

    if op_id != 0:
        insert_new_row_to_current()
    insert_to_current('player_hand', ''.join(player_hand))
    insert_to_current('dealer_hand', dealer_hand[0])
    insert_to_current('op', 'stand')
    current_time = datetime.datetime.now()
    insert_to_current('time', current_time)
    op_id += 1

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


@app.route('/flush_current_to_db', methods=['POST'])
def flush_current_to_db():
    conn = create_connection()
    c = conn.cursor()
    # if current_game is empty and reached here that means that the game ended when reealing the second card of the delaer.
    # we check in the following query if its empty.
    c.execute("SELECT op FROM current_game")
    check = c.fetchone()
    if check == (None,):
        insert_to_current('player_hand', ''.join(player_hand))
        insert_to_current('dealer_hand', dealer_hand[0])
        insert_to_current('op', 'stand')
        current_time = datetime.datetime.now()
        insert_to_current('time', current_time)

    # update rows with the correct player_win field
    winner = request.form['winner']
    c.execute('UPDATE current_game SET player_win= ?', (winner,))

    # insert rows from current-game into games
    c.execute("INSERT INTO games SELECT * FROM current_game")
    # commit the changes and close the connection
    conn.commit()
    conn.close()
    return json.dumps(0)


@app.route('/insert_to_current')
def insert_to_current(column, value):
    check_column_validity(column)
    conn = create_connection()
    c = conn.cursor()

    query = f'UPDATE current_game SET {column} = ? WHERE op_id= ? AND game= ?'
    c.execute(query, (value, op_id, game))
    # commit the changes and close the connection
    conn.commit()
    conn.close()


def insert_new_row_to_current():
    conn = create_connection()
    c = conn.cursor()
    # insert rows from current-game into games
    c.execute('INSERT INTO current_game (game, op_id) VALUES (?, ?)', (game, op_id))
    # commit the changes and close the connection
    conn.commit()
    conn.close()


def check_column_validity(column):
    valid_columns = ['game', 'op_id', 'op', 'time',
                     'player_hand', 'dealer_hand', 'player_win']
    if column in valid_columns:
        return True
    raise sqlite3('invalid column name')


# --------------------------------------------- Statistics --------------------------------------------- #

@app.route('/display_statistics')
def statistics():
    similar_hands_message = f'I saw this hand {wins + ties + losses} times.\nPlayer won: {wins} times\nPlayer lost: {losses} times\nPlayer tied: {ties} times\n'
    winning_rate_message = f'In this position:\nhit me win rate : {hit_me_win_rate:.2f} %\nstand win rate : {stand_win_rate:.2f} %\n'
    message_tuple = (similar_hands_message, winning_rate_message)
    return json.dumps(message_tuple)


@app.route('/calculate_statistics')
def calculate_statistics():
    global wins, ties, losses, hit_me_win_rate, stand_win_rate
    wins, ties, losses = find_similar_hands()
    hit_me_win_rate, stand_win_rate = find_winning_rate()
    return json.dumps(0)


def find_similar_hands():
    global wins
    conn = create_connection()
    c = conn.cursor()
    # finds the current player's hand
    player_hand_str = ''.join(player_hand)
    # finds the current dealer's hand
    dealer_hand_str = dealer_hand[0]
    # finds the number of wins.ties and losses for the current player and dealer hands
    query = '''SELECT COUNT(*) FROM (SELECT * FROM games WHERE player_hand = ? AND dealer_hand = ? AND player_win = ? GROUP BY game)'''
    c.execute(query, (player_hand_str, dealer_hand_str, 1))
    wins = c.fetchone()
    if wins is None:
        wins = 0
    else:
        wins = wins[0]
    c.execute(query, (player_hand_str, dealer_hand_str, 0))
    ties = c.fetchone()
    if ties is None:
        ties = 0
    else:
        ties = ties[0]
    c.execute(query, (player_hand_str, dealer_hand_str, -1))
    losses = c.fetchone()
    if losses is None:
        losses = 0
    else:
        losses = losses[0]

    conn.commit()
    conn.close()

    print(
        f'I saw this hand {wins + ties + losses} times\nThe player won: {wins} times, lost: {losses} and tied: {ties}\n')

    return (wins, ties, losses)


def find_winning_rate():
    conn = create_connection()
    c = conn.cursor()
    # finds the current player's hand
    player_hand_str = ''.join(player_hand)
    # finds the current dealer's hand
    dealer_hand_str = dealer_hand[0]
    # finds the number of wins when performing 'hit me' in this position

    query = '''SELECT COUNT(*) FROM (SELECT * FROM games WHERE player_hand = ? AND dealer_hand = ? AND player_win = 1 AND op = ? GROUP BY game)'''
    c.execute(query, (player_hand_str, dealer_hand_str, 'hit me'))
    hit_me_wins = c.fetchone()
    if hit_me_wins is None:
        hit_me_wins = 0
    else:
        hit_me_wins = hit_me_wins[0]

    c.execute(query, (player_hand_str, dealer_hand_str, 'stand'))
    stand_wins = c.fetchone()
    if stand_wins is None:
        stand_wins = 0
    else:
        stand_wins = stand_wins[0]

    conn.commit()
    conn.close()

    try:
        hit_me_win_rate = (hit_me_wins / wins) * 100
    except ZeroDivisionError:
        hit_me_win_rate = 0
    try:
        stand_win_rate = (stand_wins / wins) * 100
    except ZeroDivisionError:
        stand_win_rate = 0
    print(
        f'In this position:\nhit me has a win rate of: {hit_me_win_rate} %\nstand has a win rate of: {stand_win_rate} %\n')

    return (hit_me_win_rate, stand_win_rate)


if __name__ == '__main__':
    app.run(debug=True)
