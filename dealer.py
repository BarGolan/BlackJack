import random

cards = []
player_hand = []
dealer_hand = []


def main():
    create_new_deck()
    deal()
    while(True):
        command = input("choose hit me or stand:\n")
        if command == 'hit me':
            dealPlayer()
            if all(sum > 21 for sum in sum(player_hand)):
                print('Bust! You Lost')
                return
        elif command == 'stand':
            dealDealer()
            dealer_max = max(sum(dealer_hand))
            player_max = max(sum(player_hand))
            if dealer_max > player_max:
                print('You Lost! Dealer has a better hand')
                return
            elif dealer_max < player_max:
                print('You Won! You have a better hand')
                return
            else:
                print('Split! you and the dealer have equal hands')
                return
        else:
            input('invalid input try again:\n')


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

    print(f'Dealer: {dealer_hand}   sum is {sum(dealer_hand)}')
    print(f'Player: {player_hand}   sum is {sum(player_hand)}')


def dealPlayer():
    random_card = random.randint(0, len(cards) - 1)
    player_hand.append(cards.pop(random_card))
    print(f'Player: {player_hand}   sum is {sum(player_hand)}')


def dealDealer():
    while (sum(dealer_hand)[0] <= 16):
        random_card = random.randint(0, len(cards) - 1)
        dealer_hand.append(cards.pop(random_card))
        print(f'Dealer: {dealer_hand}   sum is {sum(dealer_hand)}')
        if all(sum > 21 for sum in sum(player_hand)):
            print('Bust! Dealer Lost you Won!')
            return


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


if __name__ == '__main__':
    main()
