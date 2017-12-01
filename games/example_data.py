from random import randint, choice

EMPTY_BOARD = [
    [None for _ in range(15)]
    for __ in range(15)
]

OWNER = 'o'
GUEST = 'g'


def moves_for_horizontal_win():
    """
    Generates moves for win with horizontal winner positioning, example:
     _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
     _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
     _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
     o o o o o _ _ _ _ _ _ _ _ _ _
     _ _ _ _ _ _ _ _ _ _ _ _ _ g _
     _ _ _ _ _ _ _ _ _ _ g _ _ _ _
     _ _ _ _ _ _ _ _ _ _ _ g _ _ _
     _ _ _ _ _ _ _ _ _ g _ _ _ _ _
     _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
     _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
     _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
     _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
     _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
     _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
     _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

    """
    column = randint(0, 14)
    winning_moves = [(column, y) for y in range(5)]
    losing_moves = [
        ((column + 1 + x) if column < 7 else (column - 1 - x), randint(x, 14))
        for x in range(4)
    ]
    return winning_moves, losing_moves


def moves_for_vertical_win():
    """
    Generates moves for win with vertical winner positioning, example:
     _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
     _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
     _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
     _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
     _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
     _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
     _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
     _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
     _ _ _ _ _ _ _ g _ _ _ _ _ _ _
     _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
     _ _ _ _ _ o _ _ _ _ _ _ _ _ _
     _ _ _ _ _ o g _ _ _ _ _ _ _ _
     _ _ _ _ _ o _ _ _ _ _ _ _ _ _
     _ _ _ _ _ o _ _ _ g _ _ _ _ _
     _ _ _ _ _ o _ _ g _ _ _ _ _ _

    """
    row = randint(0, 14)
    winning_moves = [(14 - y, row) for y in range(5)]
    losing_moves = [
        (randint(x, 14), (row + 1 + x) if row < 7 else (row - 1 - x),)
        for x in range(4)
    ]
    return winning_moves, losing_moves


def moves_for_diagonal_1_win():
    """
    Generates moves for win with winner positioning on first diagonal, example:
     _ _ _ _ o _ _ _ _ _ _ _ _ _ _
     _ _ _ _ _ o _ _ _ _ _ _ _ _ _
     _ _ _ _ _ _ o _ _ _ _ _ _ _ _
     _ _ _ _ _ _ _ o _ _ _ _ _ _ _
     _ _ _ _ _ _ _ _ o _ _ _ _ _ _
     _ _ _ _ _ _ _ _ _ g _ _ _ _ _
     _ _ _ _ _ _ _ _ _ _ g _ _ _ _
     _ _ _ _ _ _ _ _ _ _ _ g _ _ _
     _ _ _ _ _ _ _ _ _ _ _ _ g _ _
     _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
     _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
     _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
     _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
     _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
     _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

    """
    start_from_x, start_from_y = randint(4, 10), randint(4, 10)
    go_to = choice([1, -1])
    winning_moves = [
        (start_from_x + (m * go_to), start_from_y + (m * go_to))
        for m in range(5)
    ]
    losing_moves = [
        (start_from_x + (-m * go_to), start_from_y + (-m * go_to))
        for m in range(1, 5)
    ]
    return winning_moves, losing_moves


def moves_for_diagonal_2_win():
    """
    Generates moves for win with winner positioning on second diagonal, example:
     _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
     _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
     _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
     _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
     _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
     _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
     _ _ _ _ _ _ _ _ _ _ _ _ _ _ o
     _ _ _ _ _ _ _ _ _ _ _ _ _ o _
     _ _ _ _ _ _ _ _ _ _ _ _ o _ _
     _ _ _ _ _ _ _ _ _ _ _ o _ _ _
     _ _ _ _ _ _ _ _ _ _ o _ _ _ _
     _ _ _ _ _ _ _ _ _ g _ _ _ _ _
     _ _ _ _ _ _ _ _ g _ _ _ _ _ _
     _ _ _ _ _ _ _ g _ _ _ _ _ _ _
     _ _ _ _ _ _ g _ _ _ _ _ _ _ _

    """
    start_from_x, start_from_y = randint(4, 10), randint(4, 10)

    go_to = choice([1, -1])
    winning_moves = [
        (start_from_x + (m * go_to), start_from_y + (-m * go_to))
        for m in range(5)
    ]
    losing_moves = [
        (start_from_x + (-m * go_to), start_from_y + (m * go_to))
        for m in range(1, 5)
    ]
    return winning_moves, losing_moves


MAP_MOVES = {
    'horizontal': moves_for_horizontal_win,
    'vertical': moves_for_vertical_win,
    'diagonal_1': moves_for_diagonal_1_win,
    'diagonal_2': moves_for_diagonal_2_win,
}


def win_board(first=OWNER, win_at='horizontal'):
    second = GUEST if first == OWNER else OWNER

    winning_moves, losing_moves = MAP_MOVES[win_at]()

    def token(x, y):
        return first if (x, y) in winning_moves else second

    with_moves = set(winning_moves + losing_moves)
    assert len(with_moves) == 9

    board = [
        [token(x, y) if (x, y) in with_moves else None for y in range(15)]
        for x in range(15)
    ]

    return board, (winning_moves, losing_moves)


def draw_board(first=OWNER):
    second = GUEST if first == OWNER else OWNER

    board = [
        [first if (x + (y // 3 % 2)) % 2 == 0 and (x, y) != (14, 14) else second
         for y in range(15)] for x in range(15)
    ]
    moves = (
        [(x, y) for y in range(15) for x in range(15)
         if (x + (y // 3 % 2)) % 2 == 0 and (x, y) != (14, 14)],
        [(x, y) for y in range(15) for x in range(15)
         if (x + (y // 3 % 2)) % 2 == 1 or (x, y) == (14, 14)]
    )

    return board, moves


BASE_GAME_DICT = {
    'id': None,
    'board': EMPTY_BOARD,
    'players_count': 1,
    'players': None,
    'started': False,
    'finished': False,
    'surrendered': False,
    'draw': False,
}

BASE_PLAYER_DICT = {
    'name': None,
    'won': False,
    'owner': True,
    'first': False,
    'user': None,
    'game': None,
}


def base_game_dict(game_id, player):
    game_dict = BASE_GAME_DICT.copy()
    game_dict['id'] = game_id

    game_dict['players'] = [base_player_dict(game_id, player)]

    return game_dict


def base_player_dict(game_id, player, owner=True):
    player_dict = BASE_PLAYER_DICT.copy()
    player_dict['name'] = player.username
    player_dict['user'] = player.id
    player_dict['game'] = game_id
    player_dict['owner'] = owner
    return player_dict


ERROR_ALREADY_JOINED = {'error': 'You are already a player in this game.'}
ERROR_GAME_FULL = {'error': 'This game is already full.'}
ERROR_NOT_IN_GAME = {'error': 'You are not participating in this game.'}
ERROR_GAME_ACTIVE = {
    'error': 'This operation cannot be performed while game is active.'
}
ERROR_NOT_TURN = {'error': "It's not your turn to move"}
ERROR_SPOT_TAKEN = {'error': 'This spot is already taken.'}
