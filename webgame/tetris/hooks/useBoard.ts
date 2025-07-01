
import { useState, useEffect } from 'react';
import { createBoard, BoardType, Player } from '../gameHelpers';

export const useBoard = (player: Player, resetPlayer: () => void): { board: BoardType, setBoard: React.Dispatch<React.SetStateAction<BoardType>>, rowsCleared: number } => {
    const [board, setBoard] = useState(createBoard());
    const [rowsCleared, setRowsCleared] = useState(0);

    useEffect(() => {
        setRowsCleared(0);

        const sweepRows = (newBoard: BoardType): BoardType => {
            const ack: BoardType = [];
            let clearedCount = 0;
            newBoard.forEach(row => {
                if (row.findIndex(cell => cell[0] === 0) === -1) {
                    clearedCount += 1;
                    ack.unshift(new Array(newBoard[0].length).fill([0, 'clear']));
                } else {
                    ack.push(row);
                }
            });
            if (clearedCount > 0) {
              setRowsCleared(clearedCount);
            }
            return ack;
        }

        const updateBoard = (prevBoard: BoardType): BoardType => {
            if (!player.pos) return prevBoard;

            const newBoard = prevBoard.map(
                row => row.map(cell => (cell[1] === 'clear' ? [0, 'clear'] : cell)) as typeof row
            );
            
            player.tetromino.forEach((row, y) => {
                row.forEach((value, x) => {
                    if (value !== 0) {
                        newBoard[y + player.pos.y][x + player.pos.x] = [
                            value,
                            `${player.collided ? 'merged' : 'clear'}`,
                        ];
                    }
                });
            });

            if (player.collided) {
                resetPlayer();
                return sweepRows(newBoard);
            }

            return newBoard;
        };

        setBoard(prev => updateBoard(prev));

    }, [player, resetPlayer]);

    return { board, setBoard, rowsCleared };
};