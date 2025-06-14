// Shared Navigation Component for SATY Analytics
// This file contains the navigation bar that will be consistent across all pages

class SATYNavigation {
    constructor() {
        // Determine the correct base path based on current location
        const currentPath = window.location.pathname;
        const filename = currentPath.split('/').pop();
        
        let basePath = '';
        
        // Check if we're in a subdirectory
        if (currentPath.includes('/pages/analysis/')) {
            basePath = '../../';
        } else if (currentPath.includes('/pages/')) {
            basePath = '../';
        } else {
            basePath = '';
        }
        
        this.pages = [
            { href: basePath + 'index.html', icon: 'fas fa-home', text: 'Home', id: 'home' },
            { href: basePath + 'pages/analysis/golden-gate.html', icon: 'fas fa-chart-line', text: 'GG Analysis', id: 'analysis' },
            { href: basePath + 'pages/analysis/gap-fill.html', icon: 'fas fa-chart-area', text: 'Gap Fill', id: 'gapfill' },
            { href: basePath + 'pages/ml.html', icon: 'fas fa-brain', text: 'ML', id: 'ml' }
        ];
    }

    // Get the current page identifier from the URL
    getCurrentPage() {
        const path = window.location.pathname;
        const filename = path.split('/').pop() || 'index.html';
        
        // Map filenames to page IDs
        const pageMap = {
            'index.html': 'home',
            '': 'home', // Root path
            'golden-gate.html': 'analysis',
            'gap-fill.html': 'gapfill',
            'intraday.html': 'analysis', // Also maps to analysis
            'ml.html': 'ml'
        };
        
        return pageMap[filename] || 'home';
    }

    // Generate the navigation HTML
    generateNavHTML() {
        const currentPage = this.getCurrentPage();
        
        const navLinks = this.pages.map(page => {
            const activeClass = page.id === currentPage ? ' active' : '';
            return `
                <a href="${page.href}" class="nav-link${activeClass}">
                    <i class="${page.icon}"></i> ${page.text}
                </a>
            `;
        }).join('');

        return `
            <nav class="top-nav">
                <div class="nav-container">
                    <a href="index.html" class="logo">
                        <i class="fas fa-chart-line"></i> SATY Analytics
                    </a>
                    <div class="nav-links">
                        ${navLinks}
                    </div>
                </div>
            </nav>
        `;
    }

    // Generate the navigation CSS
    generateNavCSS() {
        return `
            .top-nav {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-bottom: 1px solid rgba(52, 152, 219, 0.1);
                padding: 15px 0;
                margin-bottom: 20px;
                position: sticky;
                top: 0;
                z-index: 100;
            }

            .nav-container {
                max-width: 1200px;
                margin: 0 auto;
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0 20px;
            }

            .logo {
                font-size: 1.5rem;
                font-weight: 700;
                color: #2c3e50;
                text-decoration: none;
            }

            .nav-links {
                display: flex;
                gap: 8px;
            }

            .nav-link {
                background: transparent;
                color: #2c3e50;
                padding: 10px 16px;
                border-radius: 6px;
                text-decoration: none;
                font-weight: 500;
                font-size: 0.95rem;
                transition: all 0.2s ease;
                border: 1px solid transparent;
            }

            .nav-link:hover {
                background: #3498db;
                color: white;
                transform: translateY(-1px);
            }

            .nav-link.active {
                background: #3498db;
                color: white;
            }

            /* Keep hover consistent across all pages */
            .nav-link:hover:not(.active) {
                background: #3498db;
            }

            @media (max-width: 768px) {
                .nav-links {
                    flex-wrap: wrap;
                    gap: 4px;
                }
                
                .nav-link {
                    font-size: 0.85rem;
                    padding: 8px 12px;
                }
            }
        `;
    }

    // Initialize the navigation on page load
    init() {
        // Add navigation CSS to head
        const style = document.createElement('style');
        style.textContent = this.generateNavCSS();
        document.head.appendChild(style);

        // Add navigation HTML to body
        const navHTML = this.generateNavHTML();
        document.body.insertAdjacentHTML('afterbegin', navHTML);

        // Add page-specific body class
        const currentPage = this.getCurrentPage();
        document.body.classList.add(`page-${currentPage}`);
    }
}

// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const navigation = new SATYNavigation();
    navigation.init();
});

// Export for manual initialization if needed
window.SATYNavigation = SATYNavigation;