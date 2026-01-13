'use client';

import { memo, useCallback } from 'react';

/**
 * Props untuk komponen Sidebar
 */
interface SidebarProps {
    /** Callback ketika user memulai chat baru */
    onNewChat?: () => void;
    /** Status apakah sidebar terbuka (mobile) */
    isOpen?: boolean;
    /** Callback ketika sidebar ditutup */
    onClose?: () => void;
}

/**
 * Ikon Close (X) untuk tombol tutup sidebar
 */
const CloseIcon = memo(function CloseIcon() {
    return (
        <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
        >
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
        </svg>
    );
});

/**
 * Header Sidebar dengan judul dan tombol tutup
 */
const SidebarHeader = memo(function SidebarHeader({
    onClose
}: {
    onClose?: () => void;
}) {
    return (
        <header className="sidebar-header">
            <h1 className="sidebar-title">GadgetBot</h1>
            <button
                className="close-sidebar-btn"
                onClick={onClose}
                aria-label="Tutup menu"
                type="button"
            >
                <CloseIcon />
            </button>
        </header>
    );
});

/**
 * Ikon LinkedIn
 */
const LinkedInIcon = () => (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z" />
        <rect x="2" y="9" width="4" height="12" />
        <circle cx="4" cy="4" r="2" />
    </svg>
);

/**
 * Ikon Instagram
 */
const InstagramIcon = () => (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="2" y="2" width="20" height="20" rx="5" ry="5" />
        <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z" />
        <line x1="17.5" y1="6.5" x2="17.51" y2="6.5" />
    </svg>
);

/**
 * Ikon GitHub
 */
const GithubIcon = () => (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path>
    </svg>
);

/**
 * Footer Sidebar dengan info copyright dan link sosial
 */
const SidebarFooter = memo(function SidebarFooter() {
    const currentYear = new Date().getFullYear();

    return (
        <footer className="sidebar-footer">
            <p className="footer-text">
                Gadget Semantic AI © {currentYear}
            </p>
            <p className="footer-by">
                by Evan Kristian Pratama
            </p>
            <div className="footer-socials">
                <a
                    href="https://www.linkedin.com/in/evan-pratama-196119271/"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="social-link"
                    aria-label="LinkedIn"
                >
                    <LinkedInIcon />
                </a>
                <a
                    href="https://www.instagram.com/evankristiannn/"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="social-link"
                    aria-label="Instagram"
                >
                    <InstagramIcon />
                </a>
                <a
                    href="https://github.com/EvanKristianPratama"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="social-link"
                    aria-label="GitHub"
                >
                    <GithubIcon />
                </a>
            </div>
        </footer>
    );
});

/**
 * Overlay untuk sidebar (mobile only)
 */
const SidebarOverlay = memo(function SidebarOverlay({
    isActive,
    onClick
}: {
    isActive: boolean;
    onClick?: () => void;
}) {
    return (
        <div
            className={`sidebar-overlay ${isActive ? 'active' : ''}`}
            onClick={onClick}
            role="presentation"
            aria-hidden="true"
        />
    );
});

/**
 * Komponen Sidebar utama
 * Menampilkan navigasi samping dengan header dan footer
 */
export const Sidebar = memo(function Sidebar({
    onNewChat,
    isOpen = false,
    onClose
}: SidebarProps) {
    const handleClose = useCallback(() => {
        onClose?.();
    }, [onClose]);

    const sidebarClasses = [
        'sidebar',
        isOpen ? 'mobile-open' : ''
    ].filter(Boolean).join(' ');

    return (
        <>
            <SidebarOverlay isActive={isOpen} onClick={handleClose} />

            <aside className={sidebarClasses} role="complementary">
                <SidebarHeader onClose={handleClose} />

                <div className="sidebar-spacer" style={{ flex: 1 }} />

                <SidebarFooter />
            </aside>
        </>
    );
});
