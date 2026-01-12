import { flushSync } from 'react-dom';
import { useTheme } from '@/hooks/useTheme';

const MoonIcon = () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
    </svg>
);

const SunIcon = () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="5"></circle>
        <line x1="12" y1="1" x2="12" y2="3"></line>
        <line x1="12" y1="21" x2="12" y2="23"></line>
        <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
        <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
        <line x1="1" y1="12" x2="3" y2="12"></line>
        <line x1="21" y1="12" x2="23" y2="12"></line>
        <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
        <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
    </svg>
);

export function ThemeToggle() {
    const { theme, toggleTheme, mounted } = useTheme();

    if (!mounted) return null;

    const handleToggle = async (e: React.MouseEvent<HTMLButtonElement>) => {
        // Fallback for browsers that don't support View Transitions
        if (!document.startViewTransition) {
            toggleTheme();
            return;
        }

        const button = e.currentTarget;
        const rect = button.getBoundingClientRect();

        // Get center of button
        const x = rect.left + rect.width / 2;
        const y = rect.top + rect.height / 2;

        // Calculate radius to the furthest corner
        const endRadius = Math.hypot(
            Math.max(x, window.innerWidth - x),
            Math.max(y, window.innerHeight - y)
        );

        const transition = document.startViewTransition(() => {
            flushSync(() => {
                toggleTheme();
            });
        });

        // Wait for the pseudo-elements to be created
        await transition.ready;

        // Animate the clip-path
        // Always grow the NEW view from the click position
        const clipPath = [
            `circle(0px at ${x}px ${y}px)`,
            `circle(${endRadius}px at ${x}px ${y}px)`
        ];

        document.documentElement.animate(
            {
                clipPath: clipPath,
            },
            {
                duration: 700, // Pelan / Slower
                easing: 'ease-in-out', // Lembut / Smooth
                pseudoElement: '::view-transition-new(root)',
            }
        );
    };

    return (
        <button
            className="theme-toggle-btn"
            onClick={handleToggle}
            aria-label="Toggle theme"
            title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
        >
            {theme === 'light' ? <MoonIcon /> : <SunIcon />}
        </button>
    );
}
