import type { ButtonHTMLAttributes } from 'react';
import { pillButtonClasses, type ButtonVariant } from '../../lib/buttonStyles';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
}

export function Button({ variant = 'primary', className, type = 'button', ...props }: ButtonProps) {
  return <button type={type} className={pillButtonClasses(variant, className)} {...props} />;
}
