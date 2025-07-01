
import React from 'react';
import { BoardType } from '../gameHelpers';
import Cell from './Cell';

type Props = {
    board: BoardType;
};

const Board: React.FC<Props> = ({ board }) => {
    return (
        <div 
            className="grid w-full h-full border-4 border-gray-600 rounded-[10px] bg-gray-900"
            style={{
                gridTemplateRows: `repeat(${board.length}, 1fr)`,
                gridTemplateColumns: `repeat(${board[0].length}, 1fr)`,
            }}
        >
            {board.map((row, y) => row.map((cell, x) => <Cell key={`${y}-${x}`} type={cell[0]} />))}
        </div>
    );
};

export default Board;