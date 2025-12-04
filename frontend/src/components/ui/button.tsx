import * as React from 'react';

type Props = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'default' | 'outline';
};

export const Button: React.FC<Props> = ({ variant = 'default', className = '', ...props }) => {
  const base = 'inline-flex items-center justify-center rounded-md text-sm font-medium h-9 px-4 transition-colors border';
  const variants = {
    default: 'bg-blue-600 text-white border-blue-600 hover:bg-blue-700',
    outline: 'bg-white text-gray-900 border-gray-300 hover:bg-gray-50'
  } as const;
  return <button className={`${base} ${variants[variant]} ${className}`} {...props} />;
};
