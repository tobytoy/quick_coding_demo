
import React from 'react';
import { ArrowUturnLeftIcon, PlayIcon, PauseIcon, ArrowLeftIcon, ArrowRightIcon, ArrowUpIcon, ArrowDownIcon, ChevronDoubleDownIcon } from '@heroicons/react/24/solid';

type Props = {
    isPaused: boolean;
    isGameOver: boolean;
    onStart: () => void;
    onPause: () => void;
    onMoveLeft: () => void;
    onMoveRight: () => void;
    onRotate: () => void;
    onDrop: () => void;
    onHardDrop: () => void;
};

const GameController: React.FC<Props> = ({
    isPaused,
    isGameOver,
    onStart,
    onPause,
    onMoveLeft,
    onMoveRight,
    onRotate,
    onDrop,
    onHardDrop,
}) => {
    const iconClass = "h-8 w-8 text-white";
    const buttonClass = "bg-gray-700 hover:bg-cyan-600 active:bg-cyan-700 p-3 rounded-full shadow-lg transition duration-200 ease-in-out transform active:scale-95 disabled:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed";

    const mainAction = isGameOver ? onStart : onPause;
    const MainIcon = isGameOver ? ArrowUturnLeftIcon : (isPaused ? PlayIcon : PauseIcon);
    const mainLabel = isGameOver ? "重新開始" : (isPaused ? "繼續" : "暫停");

    const disableControls = isPaused || isGameOver;

    return (
        <div className="flex flex-col items-center gap-4 bg-gray-800 p-4 rounded-lg shadow-lg">
            <button onClick={mainAction} className="flex items-center gap-2 bg-cyan-500 hover:bg-cyan-600 text-white font-bold py-3 px-6 rounded-lg shadow-md transition duration-200 ease-in-out transform hover:scale-105">
                <MainIcon className="h-6 w-6" />
                <span>{mainLabel}</span>
            </button>

            <div className="w-full flex justify-center items-center gap-4 mt-4">
                <button onClick={onMoveLeft} disabled={disableControls} className={buttonClass} aria-label="Move Left">
                    <ArrowLeftIcon className={iconClass} />
                </button>
                <div className="flex flex-col gap-2 items-center">
                    <button onClick={onRotate} disabled={disableControls} className={buttonClass} aria-label="Rotate">
                        <ArrowUpIcon className={iconClass} />
                    </button>
                    <button onClick={onHardDrop} disabled={disableControls} className={buttonClass} aria-label="Hard Drop">
                        <ChevronDoubleDownIcon className={iconClass} />
                    </button>
                    <button onClick={onDrop} disabled={disableControls} className={buttonClass} aria-label="Drop">
                        <ArrowDownIcon className={iconClass} />
                    </button>
                </div>
                <button onClick={onMoveRight} disabled={disableControls} className={buttonClass} aria-label="Move Right">
                    <ArrowRightIcon className={iconClass} />
                </button>
            </div>
        </div>
    );
};

export default GameController;