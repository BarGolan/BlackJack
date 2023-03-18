"use strict";

let delay = 2000;
let sum = 0;

$(document).ready(function() {
    
    $("#new_game").on("click", function() {
        if (document.getElementById("player_hand")) {
            reset_screen();
        }
        create_game_screen();
        $.ajax({
            url: '/new_game',
            success: function(response) {
                console.log('game initialized successfully');

                // Displays the cards on screen
                response = JSON.parse(response);
                display_hands(response[0], 'player');
                display_hands(response[1], 'dealer');

                // Hides the second card of the dealer
                const second_card = document.getElementById("dealer-2");
                second_card.style.backgroundColor = "rgb(169, 163, 163)";
                second_card.style.color = "rgb(169, 163, 163)";


            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log('Error:', textStatus, errorzThrown);
            }
        });
    });

    $("#container").on("click", "#hit_me.commands", function() {
        const hit_me = document.querySelector("#hit_me.commands");
        const stand = document.querySelector("#stand.commands");
        $.ajax({
            url: '/dealPlayer',
            success: function(response) {
                remove_hands('player');
                response = JSON.parse(response);
                display_hands(response, 'player');

                $.ajax({
                    url: '/is_bust',
                    success: async function(response) {
                        response = JSON.parse(response);
                        if (response == 'Bust') {
                            hit_me.style.display = 'none';
                            stand.style.display = 'none';
                            await sleep(delay);
                            let message = 'Bust ! You Lost'
                            game_over(message, 'player');
                        }
                    },
                    error: function(jqXHR, textStatus, errorThrown) {
                        console.log('Error:', textStatus, errorThrown);
                    }
                });
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log('Error:', textStatus, errorThrown);
            }
        });
    });

    $("#container").on("click", "#stand.commands", async function() {
        const stand = document.querySelector("#stand.commands");
        const hit_me = document.querySelector("#hit_me.commands");
        const lamp = document.querySelector("#statistics");
        const lamp_text = document.querySelector("p");

        hit_me.style.display = 'none';
        stand.style.display = 'none';
        if (lamp_text != null) {
            lamp_text.style.display = 'none';
        }
        lamp.style.display = 'none';
        $.ajax({
            url: '/init_dealer_sum',
            async: false,
            success: async function(response) {
                response = JSON.parse(response);
                let init_sum = response;
                if (init_sum > 16 & init_sum <=21) {
                    // Reveals the second card of the dealer
                    const second_card = document.querySelector("#dealer-2.dealer-cards");
                    second_card.style.backgroundColor = "transparent";
                    second_card.style.color = "black";
                    await sleep(delay);
                    check_winner_no_bust();
                } else {
                    $.ajax({
                            url: '/dealDealer',
                            async: false,
                            success: async function(response) {
                                // Reveals the second card of the dealer
                                const second_card = document.querySelector("#dealer-2.dealer-cards");
                                second_card.style.backgroundColor = "transparent";
                                second_card.style.color = "black";
                            
                                remove_hands('dealer');
                                response = JSON.parse(response);
                                sum = response[1];
                                display_hands(response[0], 'dealer');
                                await sleep(delay);
                                check_winner();
                        },
                        error: function(jqXHR, textStatus, errorThrown) {
                            console.log('Error:', textStatus, errorThrown);
                        }
                    }); 
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log('Error:', textStatus, errorThrown);
            }
        });

    });

    $("#statistics").on("click", function() {
        $.ajax({
            url: '/statistics',
            success: function(response) {
                console.log('caculating statistics');
                response = JSON.parse(response);
                response[0] = response[0].toString().replace(/\n/g, "<br>");
                response[1] = response[1].toString().replace(/\n/g, "<br>");
                //Checks if stat_div already exists
                let stat_div = document.getElementById("stat_div")
                if (stat_div == null) {
                    stat_div = document.createElement("div");
                    stat_div.id = "stat_div";
                    stat_div.innerHTML = '<p> ' + response[0] + '<br>' + response[1] + ' </p>';
                    document.body.appendChild(stat_div);
                } else {
                    stat_div.remove();
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log('Error:', textStatus, errorThrown);
            }
        });
    });
});

function create_game_screen() {
    // Get the element where the divs will be added
    const container = document.getElementById("container");

    // Create div for the player's hand
    const player_hand = document.createElement("div");
    player_hand.setAttribute("id", `player_hand`);
    player_hand.setAttribute("class", "hands");
    player_hand.textContent = `Player`;
    container.appendChild(player_hand)

    // Create div for the dealer's hand
    const dealer_hand = document.createElement("div");
    dealer_hand.setAttribute("id", `dealer_hand`);
    dealer_hand.setAttribute("class", "hands");
    dealer_hand.textContent = `Dealer`;
    container.appendChild(dealer_hand)

    // Create 'hit me' and 'stand' buttons

    const commands = document.createElement("div");
    commands.setAttribute("class", "commands");
    container.appendChild(commands)

    const hit_me = document.createElement("button");
    hit_me.setAttribute("id", `hit_me`);
    hit_me.setAttribute("class", "commands");
    hit_me.textContent = `Hit me`;
    commands.appendChild(hit_me)

    const stand = document.createElement("button");
    stand.setAttribute("id", `stand`);
    stand.setAttribute("class", "commands");
    stand.textContent = `Stand`;
    commands.appendChild(stand)
   
    const lamp = document.getElementById("statistics");
    lamp.style.display = 'block';

    const new_game = document.getElementById("new_game");
    new_game.style.display = 'none';
}

function display_hands(cards, parent) {
    const hand = document.getElementById(`${parent}_hand`);

    // Loop to create and append each card to its parent
    for (let i = 1; i <= cards.length; i++) {
        const card = document.createElement("div");
        card.setAttribute("id", `${parent}-${i}`);
        card.setAttribute("class", `${parent}-cards`);
        card.textContent = cards[i - 1];
        hand.appendChild(card)
    }
}

function remove_hands(parent) {
    const hand = document.getElementById(`${parent}_hand`);
    const children = hand.querySelectorAll(`.${parent}-cards`); // replace 'childID' with the ID of the child elements you want to remove

    children.forEach(child => child.remove());
}

function write_to_screen(message, parent) {
    remove_hands(parent);
    const hand = document.getElementById(`${parent}_hand`);

    const message_card = document.createElement("div");
    message_card.setAttribute("id", "message-card");
    message_card.setAttribute("class", `${parent}-cards`);
    message_card.textContent = message;
    hand.appendChild(message_card)

}

function game_over(message, parent) {
    console.log(message);
    write_to_screen(message, parent)
    let winner = evaluate_message(message)

    $.ajax({
        url: '/flush_current_to_db',
        type: 'POST',
        data: { winner: winner },
        success: function(response) {
            console.log('inserting game table to gambler db');
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log('Error:', textStatus, errorThrown);
        }
    });

    const new_game = document.getElementById("new_game");
    new_game.style.display = 'block';
}

function reset_screen() {
    const player_hand = document.getElementById('player_hand');
    const dealer_hand = document.getElementById('dealer_hand');
    const commands = document.querySelector('.commands');
    player_hand.remove();
    dealer_hand.remove();
    commands.remove();
    sum = 0
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function check_winner() {
    if (sum > 21) {
        console.log('sum > 21');
        let message = 'Bust! Dealer Lost you Won!';
        game_over(message, 'dealer');
    } else if (sum <= 16) {
        console.log('sum <= 16');
        const stand = document.querySelector("#stand.commands");
        stand.click();
    } else {
        console.log('else');
        check_winner_no_bust();
    }
}

function check_winner_no_bust() {
    $.ajax({
        url: '/winner',
        success: function(response) {
            let message = JSON.parse(response);
            game_over(message, 'dealer');
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log('Error:', textStatus, errorThrown);
        }
    });
}

function evaluate_message(message) {
    // Checks for messages where the dealer wins
    if (message === 'Bust ! You Lost' || message == 'You Lost! Dealer has a better hand') {
        return -1;
    // Checks for messages where the player wins
    } else if (message === 'Bust! Dealer Lost you Won!' || message === 'You Won! You have a better hand') {
        return 1;
    // Checks for messages where the player and the dealer are tied and split
    } else if (message === 'Split! you and the dealer have equal hands') {
        return 0;
    }
}




