
import { useState, useCallback } from 'react';
import { randomTetromino, TETROMINOS, BOARD_WIDTH, checkCollision, BoardType } from '../gameHelpers';

type PlayerState = {
    pos: { x: number, y: number };
    tetromino: (string | number)[][];
    collided: boolean;
};

type NextPiece = keyof typeof TETROMINOS;

export const usePlayer = (): { 
    player: PlayerState, 
    nextPiece: NextPiece, 
    updatePlayerPos: (pos: {x: number, y: number, collided: boolean}) => void,
    resetPlayer: () => void,
    playerRotate: (board: BoardType, dir: number) => void
} => {
    const [player, setPlayer] = useState<PlayerState>({
        pos: { x: 0, y: 0 },
        tetromino: TETROMINOS[0].shape,
        collided: false,
    });
    
    const [nextPiece, setNextPiece] = useState<NextPiece>(randomTetromino().shape[1][1] as NextPiece);

    const rotate = (matrix: (string|number)[][], dir: number) => {
        const rotatedTetro = matrix.map((_, index) => matrix.map(col => col[index]));
        if (dir > 0) return rotatedTetro.map(row => row.reverse());
        return rotatedTetro.reverse();
    }

    const playerRotate = (board: BoardType, dir: number) => {
        const clonedPlayer = JSON.parse(JSON.stringify(player));
        clonedPlayer.tetromino = rotate(clonedPlayer.tetromino, dir);

        const pos = clonedPlayer.pos.x;
        let offset = 1;
        while(checkCollision(clonedPlayer, board, { x: 0, y: 0 })) {
            clonedPlayer.pos.x += offset;
            offset = -(offset + (offset > 0 ? 1 : -1));
            if (offset > clonedPlayer.tetromino[0].length) {
                rotate(clonedPlayer.tetromino, -dir);
                clonedPlayer.pos.x = pos;
                return;
            }
        }
        setPlayer(clonedPlayer);
    }

    const updatePlayerPos = useCallback(({ x, y, collided }: { x: number, y: number, collided: boolean }) => {
        setPlayer(prev => ({
            ...prev,
            pos: { x: (prev.pos.x += x), y: (prev.pos.y += y) },
            collided,
        }));
    }, []);

    const resetPlayer = useCallback(() => {
        const newPieceShape = nextPiece ? TETROMINOS[nextPiece].shape : randomTetromino().shape;
        const newNextPieceKey = randomTetromino().shape[1][1] as NextPiece;
        
        setPlayer({
            pos: { x: BOARD_WIDTH / 2 - 1, y: 0 },
            tetromino: newPieceShape,
            collided: false,
        });

        setNextPiece(newNextPieceKey);
    }, [nextPiece]);

    return { player, nextPiece, updatePlayerPos, resetPlayer, playerRotate };
};