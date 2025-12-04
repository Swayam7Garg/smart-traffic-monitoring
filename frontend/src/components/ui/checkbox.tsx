import * as React from 'react';

type Props = Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type' | 'onChange'> & {
  onCheckedChange?: (checked: boolean) => void;
};

export const Checkbox: React.FC<Props> = ({ onCheckedChange, className='', ...props }) => (
  <input type="checkbox" className={`h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 ${className}`}
         onChange={(e)=> onCheckedChange?.(e.target.checked)} {...props} />
);
