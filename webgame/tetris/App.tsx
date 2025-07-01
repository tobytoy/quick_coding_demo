
import React, { useState, useCallback, useEffect } from 'react';
import { usePlayer } from './hooks/usePlayer';
import { useBoard } from './hooks/useBoard';
import { useInterval } from './hooks/useInterval';
import { useGameStatus } from './hooks/useGameStatus';
import { createBoard, checkCollision } from './gameHelpers';
import Board from './components/Board';
import Display from './components/Display';
import GameController from './components/GameController';
import NextPiece from './components/NextPiece';

const App: React.FC = () => {
    const [dropTime, setDropTime] = useState<number | null>(null);
    const [isPaused, setIsPaused] = useState<boolean>(false);
    const [gameOver, setGameOver] = useState<boolean>(true);

    const { player, updatePlayerPos, resetPlayer, playerRotate, nextPiece } = usePlayer();
    const { board, setBoard, rowsCleared } = useBoard(player, resetPlayer);
    const { score, setScore, rows, setRows, level, setLevel } = useGameStatus(rowsCleared);

    const movePlayer = (dir: number) => {
        if (!checkCollision(player, board, { x: dir, y: 0 })) {
            updatePlayerPos({ x: dir, y: 0, collided: false });
        }
    };
    
    const startGame = useCallback(() => {
        setBoard(createBoard());
        setDropTime(1000);
        resetPlayer();
        setGameOver(false);
        setScore(0);
        setRows(0);
        setLevel(0);
        setIsPaused(false);
    }, [resetPlayer, setBoard, setLevel, setRows, setScore]);

    const pauseGame = () => {
        if (!gameOver) {
            setIsPaused(prev => !prev);
            setDropTime(isPaused ? 1000 / (level + 1) + 200 : null);
        }
    };

    const drop = () => {
        if (isPaused) return;

        if (rows > (level + 1) * 10) {
            setLevel(prev => prev + 1);
            setDropTime(1000 / (level + 1) + 200);
        }

        if (!checkCollision(player, board, { x: 0, y: 1 })) {
            updatePlayerPos({ x: 0, y: 1, collided: false });
        } else {
            if (player.pos.y < 1) {
                setGameOver(true);
                setDropTime(null);
                return;
            }
            updatePlayerPos({ x: 0, y: 0, collided: true });
        }
    };

    const keyUp = ({ keyCode }: { keyCode: number }): void => {
        if (!gameOver && !isPaused) {
            if (keyCode === 40) { // Down arrow
                setDropTime(1000 / (level + 1) + 200);
            }
        }
    };

    const dropPlayer = () => {
        setDropTime(null);
        drop();
    };
    
    const hardDrop = () => {
        if (isPaused) return;
        let tempY = 0;
        while (!checkCollision(player, board, { x: 0, y: tempY + 1 })) {
            tempY++;
        }
        updatePlayerPos({ x: 0, y: tempY, collided: true });
    }

    const move = ({ keyCode }: { keyCode: number }): void => {
        if (!gameOver && !isPaused) {
            if (keyCode === 37) { // Left arrow
                movePlayer(-1);
            } else if (keyCode === 39) { // Right arrow
                movePlayer(1);
            } else if (keyCode === 40) { // Down arrow
                dropPlayer();
            } else if (keyCode === 38) { // Up arrow
                playerRotate(board, 1);
            } else if (keyCode === 32) { // Space bar for hard drop
                hardDrop();
            }
        }
    };

    useInterval(drop, dropTime);

    useEffect(() => {
        window.addEventListener('keydown', move);
        window.addEventListener('keyup', keyUp);

        return () => {
            window.removeEventListener('keydown', move);
            window.removeEventListener('keyup', keyUp);
        };
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [isPaused, gameOver, player, board, level]);

    return (
        <div className="min-h-screen bg-gray-900 text-gray-200 flex flex-col items-center justify-center p-4 font-mono" role="button" tabIndex={0} onKeyDown={e => move(e)} onKeyUp={keyUp}>
            <div className="w-full max-w-4xl mx-auto flex flex-col md:flex-row gap-8 items-start justify-center">
                <div className="relative w-[340px] h-[640px] md:w-[400px] md:h-[720px]">
                    <Board board={board} />
                    {(gameOver || isPaused) && (
                         <div className="absolute inset-0 bg-black bg-opacity-75 flex flex-col items-center justify-center z-10">
                            {gameOver && <h2 className="text-4xl font-bold text-red-500 mb-4">遊戲結束</h2>}
                            {isPaused && !gameOver && <h2 className="text-4xl font-bold text-yellow-400 mb-4">已暫停</h2>}
                         </div>
                    )}
                </div>
                
                <aside className="w-full md:w-52 flex flex-col gap-6">
                    <div className="bg-gray-800 p-4 rounded-lg shadow-lg">
                        <Display text={`分數: ${score}`} />
                        <Display text={`行數: ${rows}`} />
                        <Display text={`等級: ${level}`} />
                    </div>
                    {nextPiece && <NextPiece nextPiece={nextPiece} />}
                    <GameController
                        isPaused={isPaused}
                        isGameOver={gameOver}
                        onStart={startGame}
                        onPause={pauseGame}
                        onMoveLeft={() => movePlayer(-1)}
                        onMoveRight={() => movePlayer(1)}
                        onRotate={() => playerRotate(board, 1)}
                        onDrop={dropPlayer}
                        onHardDrop={hardDrop}
                    />
                </aside>
            </div>
            <div className="hidden md:block text-gray-400 mt-8 text-center">
                <h3 className="text-lg font-bold mb-2">控制</h3>
                <p>左/右箭頭: 移動</p>
                <p>上箭頭: 旋轉</p>
                <p>下箭頭: 軟降</p>
                <p>空白鍵: 硬降</p>
            </div>
        </div>
    );
};

export default App;