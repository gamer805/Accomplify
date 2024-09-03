import React, { ReactNode } from 'react';

interface ButtonProps {
    children: ReactNode;
    onClick: () => void;
    className?: string;
}

// Simple Button component
export const Button: React.FC<ButtonProps> = ({ children, onClick, className = '' }) => (
    <button
        onClick={onClick}
        className={`px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 ${className}`}
    >
        {children}
    </button>
);