
export const BOARD_WIDTH = 12;
export const BOARD_HEIGHT = 20;

export type BoardCell = [string | number, string];
export type BoardType = BoardCell[][];
export type Player = {
    pos: { x: number, y: number },
    tetromino: (string | number)[][],
    collided: boolean,
};

export const createBoard = (): BoardType =>
    Array.from(Array(BOARD_HEIGHT), () =>
        new Array(BOARD_WIDTH).fill([0, 'clear'])
    );

type TetrominoShape = {
    shape: (string | number)[][];
    color: string;
};

type Tetrominos = {
    [key: string | number]: TetrominoShape;
};

export const TETROMINOS: Tetrominos = {
    0: { shape: [[0]], color: '0, 0, 0' },
    I: {
        shape: [
            [0, 'I', 0, 0],
            [0, 'I', 0, 0],
            [0, 'I', 0, 0],
            [0, 'I', 0, 0]
        ],
        color: '80, 227, 230', // Cyan
    },
    J: {
        shape: [
            [0, 'J', 0],
            [0, 'J', 0],
            ['J', 'J', 0]
        ],
        color: '36, 95, 223', // Blue
    },
    L: {
        shape: [
            [0, 'L', 0],
            [0, 'L', 0],
            [0, 'L', 'L']
        ],
        color: '223, 173, 36', // Orange
    },
    O: {
        shape: [
            ['O', 'O'],
            ['O', 'O']
        ],
        color: '223, 217, 36', // Yellow
    },
    S: {
        shape: [
            [0, 'S', 'S'],
            ['S', 'S', 0],
            [0, 0, 0]
        ],
        color: '48, 211, 56', // Green
    },
    T: {
        shape: [
            [0, 0, 0],
            ['T', 'T', 'T'],
            [0, 'T', 0]
        ],
        color: '132, 61, 198', // Purple
    },
    Z: {
        shape: [
            ['Z', 'Z', 0],
            [0, 'Z', 'Z'],
            [0, 0, 0]
        ],
        color: '227, 78, 78', // Red
    }
};

export const randomTetromino = (): TetrominoShape => {
    const tetrominos = 'IJLOSTZ';
    const randTetromino = tetrominos[Math.floor(Math.random() * tetrominos.length)];
    return TETROMINOS[randTetromino];
};

export const checkCollision = (player: Player, board: BoardType, { x: moveX, y: moveY }: { x: number, y: number }): boolean => {
    for (let y = 0; y < player.tetromino.length; y += 1) {
        for (let x = 0; x < player.tetromino[y].length; x += 1) {
            if (player.tetromino[y][x] !== 0) {
                if (
                    !board[y + player.pos.y + moveY] ||
                    !board[y + player.pos.y + moveY][x + player.pos.x + moveX] ||
                    board[y + player.pos.y + moveY][x + player.pos.x + moveX][1] !== 'clear'
                ) {
                    return true;
                }
            }
        }
    }
    return false;
};