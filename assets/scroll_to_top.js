// assets/scroll_to_top.js

if (!window.__scrollToTopInstalled) {
    window.__scrollToTopInstalled = true;

    (function(history) {
        const pushState = history.pushState;
        const replaceState = history.replaceState;

        history.pushState = function() {
            const ret = pushState.apply(this, arguments);
            window.dispatchEvent(new Event('locationchange'));
            return ret;
        };

        history.replaceState = function() {
            const ret = replaceState.apply(this, arguments);
            window.dispatchEvent(new Event('locationchange'));
            return ret;
        };

        window.addEventListener('popstate', function() {
            window.dispatchEvent(new Event('locationchange'));
        });
    })(window.history);

    function scrollToTopForce() {
        // On force le scroll tout en haut (sans animation)
        window.scrollTo(0, 0);
    }

    window.addEventListener('locationchange', function() {
        // 1) tout de suite
        scrollToTopForce();

        // 2) juste après le rendu de la nouvelle page
        setTimeout(scrollToTopForce, 50);

        // 3) sécurité si Dash refait un scroll plus tard
        setTimeout(scrollToTopForce, 200);
    });
}
