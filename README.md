# HAHATON API SERVER


## Board representation

Board is represented as two dimensional (or nested, whatever you prefer to call
it) array, e.g.:

```json
[
  [null, null, null],
  [null, null, null],
  [null, null, null]
]
```

But of course, in size `15x15`.

Each board field may have one of three values:
- `null` if it is still free
- `o` - if owner of the game placed his/her token there
- `g` - if guest of the game placed his/her token there

The board fields uses `x` and `y` coordinates, but to be honest the orientation
of the board doesn't matter - rotation does not change game rules :)

And of course, both `x` and `y` are indexed from `0` to `14`.

## API `/api`

**IMPORTANT NOTE**: please pay attention whether `/` is present at the end of
the url being requested! It is generally not used after `id`s.

### `/user`

#### `/register/`

Register new user.

**POST**:
```json
{
  "username": "user",
  "password": "password"
}
```
*Returns*
```json
{
  "username": "user",
  "won": 0,
  "lost": 0,
  "won_by_surrender": 0,
  "draws": 0,
  "surrendered": 0
}
```

#### `/login/`

Login existing user.

**POST**:
```json
{
  "username": "user",
  "password": "password"
}
```
*Returns*
```json
{
  "username": "user",
  "won": 0,
  "lost": 0,
  "won_by_surrender": 0,
  "draws": 0,
  "surrendered": 0
}
```

#### `/logout/`

Logout logged-in user.

**POST**
```json
{}
```
*Returns*
```
HTTP 200 OK
```

#### `/me/`

Get info about logged in user.

**GET:**
```json
{
  "username": "player_1",
  "won": 1,
  "lost": 0,
  "won_by_surrender": 0,
  "draws": 0,
  "surrendered": 0
}
```

**PATCH:**
```json
{
  "username": "player_11"
}
```
*Returns:*
```json
{
  "username": "player_11",
  "won": 1,
  "lost": 0,
  "won_by_surrender": 0,
  "draws": 0,
  "surrendered": 0
}
```

#### `/{id}`

Retrieves info about given user.

**GET:**
```json
{
  "username": "player_1",
  "won": 1,
  "lost": 0,
  "won_by_surrender": 0,
  "draws": 0,
  "surrendered": 0
}
```

#### `/me/games/`

List of user's active or waiting games.

**GET:**
```json
[
  {
    "id": 3,
    "players_count": 2,
    "players": [
      {
        "id": 2,
        "won": false,
        "owner": true,
        "first": false,
        "user": 10,
        "game": 3
      },
      {
        "id": 3,
        "won": false,
        "owner": false,
        "first": false,
        "user": 9,
        "game": 3
      }
    ],
    "started": true,
    "finished": false,
    "surrendered": false,
    "draw": false
  }
]
```

#### `/me/games/finished/`

List of user's finished games.

**GET:**
```json
[
  {
    "id": 3,
    "players_count": 2,
    "players": [
      {
        "id": 2,
        "won": true,
        "owner": true,
        "first": false,
        "user": 10,
        "game": 3
      },
      {
        "id": 3,
        "won": false,
        "owner": false,
        "first": false,
        "user": 9,
        "game": 3
      }
    ],
    "started": true,
    "finished": true,
    "surrendered": false,
    "draw": false
  }
]
```

### `/games`

#### `/`

List of recent awaiting games.

**GET:**
```json
[
  {
    "id": 2,
    "players_count": 1,
    "players": [
      {
        "id": 1,
        "name": "23",
        "won": false,
        "owner": true,
        "first": false,
        "user": 6,
        "game": 2
      }
    ],
    "started": false,
    "finished": false,
    "surrendered": false,
    "draw": false
  },
  {
    "id": 5,
    "players_count": 1,
    "players": [
      {
        "id": 5,
        "name": "player_2",
        "won": false,
        "owner": true,
        "first": false,
        "user": 9,
        "game": 5
      }
    ],
    "started": false,
    "finished": false,
    "surrendered": false,
    "draw": false
  }
]
```

Create new game.

**POST:**
```json
{}
```
*Returns:*
```
{
  "id": 4,
  "players_count": 1,
  "players": [
    {
      "id": 5,
      "name": "player_2",
      "won": false,
      "owner": true,
      "first": false,
      "user": 9,
      "game": 5
    }
  ],
  "board": [
    [
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null
    ],
    ...
  ],
  "started": false,
  "finished": false,
  "surrendered": false,
  "draw": false
}
```

#### `/{id}`

Retrieves detailed info about given game.

**GET:**
```
{
  "id": 4,
  "players_count": 1,
  "players": [
    {
      "id": 5,
      "name": "player_2",
      "won": false,
      "owner": true,
      "first": false,
      "user": 9,
      "game": 5
    }
  ],
  "board": [
    [
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null,
      null
    ],
    ...
  ],
  "started": false,
  "finished": false,
  "surrendered": false,
  "draw": false
}
```

#### `/{id}/[join|start|leave|surrender]/`

Performs given action for chosen game:
- `join` - join free player spot in game
- `start` - start game with two players joined
- `leave` - leave joined game, before it started
- `surrender` - surrender active game

**POST:**
```json
{}
```

*Returns (note: surrender does not return game info):*
```json
{
    "game": {
        "id": 2,
        "players_count": 2,
        "players": [
            {
                "id": 1,
                "name": "23",
                "won": false,
                "owner": true,
                "first": false,
                "user": 6,
                "game": 2
            },
            {
                "id": 6,
                "name": "player_1",
                "won": false,
                "owner": false,
                "first": false,
                "user": 10,
                "game": 2
            }
        ],
        "board": [
            [
                null,
                null,
                null,
                null,
                null,
                null,
                null,
                null,
                null,
                null,
                null,
                null,
                null,
                null,
                null
            ],
            ...
        ],
        "started": false,
        "finished": false,
        "surrendered": false,
        "draw": false
    },
    "success": true
}
```

#### `/{id}/moves/`

Retrieves sorted list of moves in given game.

**GET:**

```json
[
  {
    "id": 5,
    "player": 2,
    "timestamp": "2017-10-05T07:08:11.655920Z",
    "x": 1,
    "y": 4
  },
  {
    "id": 4,
    "player": 3,
    "timestamp": "2017-10-05T07:08:07.948708Z",
    "x": 0,
    "y": 1
  },
  {
    "id": 3,
    "player": 2,
    "timestamp": "2017-10-05T07:07:57.911134Z",
    "x": 1,
    "y": 3
  },
  {
    "id": 2,
    "player": 3,
    "timestamp": "2017-10-05T07:07:51.038740Z",
    "x": 0,
    "y": 0
  },
  {
    "id": 1,
    "player": 2,
    "timestamp": "2017-10-05T07:07:31.975650Z",
    "x": 1,
    "y": 2
  }
]
```

Makes next move in game:

**POST:**
```json
{
  "x": 4,
  "y": 2
}
```
*Returns:*
```json
{
  "game": {
    "id": 2,
    "players_count": 2,
    "players": [
      {
        "id": 1,
        "name": "23",
        "won": false,
        "owner": true,
        "first": false,
        "user": 6,
        "game": 2
      },
      {
        "id": 6,
        "name": "player_1",
        "won": false,
        "owner": false,
        "first": true,
        "user": 10,
        "game": 2
      }
    ],
    "board": [
      [
        "g",
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null
      ],
      ...
    ],
    "started": true,
    "finished": false,
    "surrendered": false,
    "draw": false
  },
  "move": {
    "id": 10,
    "player": 6,
    "timestamp": "2017-10-05T09:10:02.405071Z",
    "x": 0,
    "y": 0
  }
}
```

#### `/{id}/moves/last/`

Retrieves last move from given game.

**GET:**
```json

{
  "id": 10,
  "player": 6,
  "timestamp": "2017-10-05T09:10:02.405071Z",
  "x": 0,
  "y": 0
}
```
