/* Tiknix Docs — theme toggle + mobile sidebar. No dependencies. */
(function () {
    var KEY = 'tiknix-docs-theme';

    function apply(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        var icon = document.getElementById('themeIcon');
        if (icon) icon.textContent = theme === 'dark' ? '☾' : '☀';
    }

    var stored = null;
    try { stored = localStorage.getItem(KEY); } catch (e) {}
    var prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    apply(stored || (prefersDark ? 'dark' : 'light'));

    document.addEventListener('DOMContentLoaded', function () {
        apply(document.documentElement.getAttribute('data-theme'));

        var toggle = document.getElementById('themeToggle');
        if (toggle) {
            toggle.addEventListener('click', function () {
                var next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
                apply(next);
                try { localStorage.setItem(KEY, next); } catch (e) {}
            });
        }

        var sidebar = document.getElementById('sidebar');
        var backdrop = document.getElementById('sidebarBackdrop');
        function setOpen(open) {
            if (!sidebar || !backdrop) return;
            sidebar.classList.toggle('show', open);
            backdrop.classList.toggle('show', open);
        }
        var menu = document.getElementById('menuToggle');
        if (menu) menu.addEventListener('click', function () { setOpen(!sidebar.classList.contains('show')); });
        if (backdrop) backdrop.addEventListener('click', function () { setOpen(false); });

        // Keep the active nav item in view on long article lists.
        var active = document.querySelector('.nav-link.active');
        if (active && active.scrollIntoView) active.scrollIntoView({ block: 'nearest' });
    });
})();
