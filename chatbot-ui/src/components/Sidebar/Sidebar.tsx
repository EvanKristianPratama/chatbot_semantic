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
 * Footer Sidebar dengan info copyright
 */
const SidebarFooter = memo(function SidebarFooter() {
    const currentYear = new Date().getFullYear();

    return (
        <footer className="sidebar-footer">
            <p className="footer-text">
                Gadget Semantic AI
                <br />
                © {currentYear}
            </p>
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
