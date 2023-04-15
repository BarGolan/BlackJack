"use strict";

$(document).ready(function() {
    run_script();
});

async function run_script() {
    let i = 0;
    while (i < 100000) {
        console.log('starting game number: ' + i);
        await start_new_game();
        await click_buttons();
        console.log('finished game number: ' + i);
        i++;
    }
}

function click_buttons() {
    return new Promise(async (resolve, reject) => {
        while (true) {
            let current_button = get_random_button();
            let button_id = '#' + current_button;
            let button_ready = $(button_id);
            let new_game = $('#new_game');
            
            if (button_id == '#hit_me') {
                if (new_game.is(':visible')) {
                    break;
                } else {
                    button_ready.click();
                }

            } else if (button_id == '#stand') {
                if (new_game.is(':visible')) {
                    break;
                } else {
                    button_ready.click();
                    break;
                }
            }
            await sleep(2500); // wait 1 second before checking for buttons again
        }
        resolve();
    });
}

function get_random_button() {
    const buttons = ['hit_me', 'stand'];
    let index = Math.floor(Math.random() * buttons.length);
    return buttons[index];
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function start_new_game() {
    return new Promise(async (resolve, reject) => {
        while (true) {
            let new_game = $('#new_game');
            if (new_game.is(':visible')) {
                new_game.click();
                await sleep(1000); // wait 1 second before resolving the Promise
                resolve(); // resolve the Promise when the 'new game' button is clicked
                break;
            }
            await sleep(1000); // wait 1 second before checking for the button again
        }
    });
}
