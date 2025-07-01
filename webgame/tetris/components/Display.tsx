
import React from 'react';

type Props = {
    text: string;
};

const Display: React.FC<Props> = ({ text }) => (
    <div className="text-xl font-bold text-cyan-400 mb-2 p-2 bg-gray-900 rounded-md shadow-inner">
        {text}
    </div>
);

export default Display;