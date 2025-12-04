export function useToast() {
  return {
    toast: (opts: { title?: string; description?: string; variant?: 'default'|'destructive' }) => {
      if (opts?.variant === 'destructive') console.error(opts.title || 'Error');
      else console.log(opts.title || 'Info');
    }
  };
}
