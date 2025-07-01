
import React from 'react';
import Cell from './Cell';
import { TETROMINOS } from '../gameHelpers';

type Props = {
  nextPiece: keyof typeof TETROMINOS;
};

const NextPiece: React.FC<Props> = ({ nextPiece }) => {
  const { shape } = TETROMINOS[nextPiece] || TETROMINOS[0];

  // Create a 4x4 grid for display
  const displayGrid: (string|number)[][] = Array(4).fill(0).map(() => Array(4).fill(0));

  // Center the piece in the grid
  const offsetX = Math.floor((4 - shape[0].length) / 2);
  const offsetY = Math.floor((4 - shape.length) / 2);

  shape.forEach((row, y) => {
    row.forEach((value, x) => {
      if (value !== 0) {
        displayGrid[y + offsetY][x + offsetX] = value;
      }
    });
  });

  return (
    <div className="bg-gray-800 p-4 rounded-lg shadow-lg">
      <h2 className="text-xl font-bold text-cyan-400 mb-2">下一個</h2>
      <div
        className="grid grid-cols-4 grid-rows-4 w-[100px] h-[100px] mx-auto bg-gray-900 rounded-[5px] border-2 border-gray-600"
      >
        {displayGrid.map((row, y) =>
          row.map((cell, x) => <Cell key={`${y}-${x}`} type={cell} />)
        )}
      </div>
    </div>
  );
};

export default NextPiece;