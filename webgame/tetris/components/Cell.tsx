
import React from 'react';
import { TETROMINOS } from '../gameHelpers';

type Props = {
    type: string | number;
};

const Cell: React.FC<Props> = ({ type }) => {
    const color = TETROMINOS[type]?.color || '0, 0, 0';
    const isSet = type !== 0;

    const style: React.CSSProperties = {
        backgroundColor: `rgba(${color}, ${isSet ? '0.8' : '0'})`,
        border: isSet ? '4px solid' : '1px solid',
        borderColor: `rgba(${color}, ${isSet ? '1' : '0.1'})`,
        borderBottomColor: `rgba(${color}, ${isSet ? '0.1' : '0.1'})`,
        borderRightColor: `rgba(${color}, ${isSet ? '1' : '0.1'})`,
        borderTopColor: `rgba(${color}, ${isSet ? '1' : '0.1'})`,
        borderLeftColor: `rgba(${color}, ${isSet ? '0.3' : '0.1'})`,
        boxShadow: isSet ? `inset 2px 2px 5px rgba(255,255,255,0.3), inset -2px -2px 5px rgba(0,0,0,0.3)` : 'none'
    };

    return <div className="w-full aspect-square" style={style}></div>;
};

export default React.memo(Cell);