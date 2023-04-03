$(document).ready(function() {
    run_script();
  });

  let i = 0;  
  async function run_script() {
    console.log('starting game number: ' + i);
    await start_new_game();
    await click_buttons();
    console.log('finished game number: ' + i);
    i++;
    run_script();
  }
  
  async function click_buttons() {
    let current_button = get_random_button();
    let button_id = '#' + current_button;
    let j = 0;
    while (j < 10) {
      let button_ready = $(button_id);
      if (button_id == '#hit_me' && button_ready && button_ready.offsetParent !== null && button_ready.offsetWidth !== 0) {
        button_ready.click();
        button_id = '#' + get_random_button();
      }
      if (button_id == '#stand' && button_ready && button_ready.offsetParent !== null && button_ready.offsetWidth !== 0) {
        button_ready.click();
        await waitForElement('#new_game');
        return;
      }
      j++;
      await sleep(1000);
    }
  }
  
  function get_random_button() {
    const buttons = ['hit_me', 'stand'];
    let index = Math.floor(Math.random() * buttons.length);
    return buttons[index];
  }
  
  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
  
  async function start_new_game() {
    const new_game = await waitForElement('#new_game');
    new_game.click();
  }
  
  async function waitForElement(selector) {
    return new Promise(resolve => {
      const intervalId = setInterval(() => {
        const element = $(selector);
        if (element && element.offsetParent !== null && element.offsetWidth !== 0) {
          clearInterval(intervalId);
          resolve(element);
        }
      }, 1000);
    });
  }
  