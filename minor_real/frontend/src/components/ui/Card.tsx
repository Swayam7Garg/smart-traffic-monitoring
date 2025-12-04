
import { cn } from '../../lib/utils';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  glow?: 'blue' | 'green' | 'red' | 'none';
}

export const Card: React.FC<CardProps> = ({
  children,
  className,
  hover = false,
  glow = 'none',
  ...props
}) => {
  return (
    <div
      className={cn(
        'glass rounded-xl p-6 transition-all duration-300',
        hover && 'card-hover cursor-pointer',
        glow === 'blue' && 'glow-blue',
        glow === 'green' && 'glow-green',
        glow === 'red' && 'glow-red',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};

interface CardHeaderProps {
  children: React.ReactNode;
  className?: string;
}

export const CardHeader: React.FC<CardHeaderProps> = ({ children, className }) => {
  return (
    <div className={cn('flex items-center justify-between mb-4', className)}>
      {children}
    </div>
  );
};

interface CardTitleProps {
  children: React.ReactNode;
  className?: string;
}

export const CardTitle: React.FC<CardTitleProps> = ({ children, className }) => {
  return (
    <h3 className={cn('text-lg font-semibold text-slate-100', className)}>
      {children}
    </h3>
  );
};

interface CardContentProps {
  children: React.ReactNode;
  className?: string;
}

export const CardContent: React.FC<CardContentProps> = ({ children, className }) => {
  return <div className={cn('text-slate-300', className)}>{children}</div>;
};

