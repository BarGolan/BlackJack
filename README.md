# Black Jack

## _This app allows the user to play black jack against the dealer_

### Features

- The app allows a player to play Black Jack against a dealer.
  <br>
- On each move it is possible to hit the light bulb button and recive statistics about the current hand. In addition, it supplies with recommendations of the correct moves leaning on information of past hands seen by the app and stored in the db.

## Running the program

Running from command:
This is a flask app, therefore it can run from the command line by typing:

```sh

flask run
```

Than opening the browser on the url supplied in the terminal which is the local server's url

```sh
http://127.0.0.1:5000/
```

## Auto-play

- Mostly for development purposes and in order to enlarge the db (number of hands in the db), it is possible to run a script which plays the game automatically, randomly, repetedely.

- This can be done by uncommenting the marked line in the 'index.html' file:

![index.html header](/static/images/index.html_header.png)
