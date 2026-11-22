// Cookie banner. The consent defaults (all denied) and a returning visitor's
// stored choice are applied by the inline script in base.html <head>, before
// Tag Manager and AdSense load. This file shows the banner and records choices.
(function () {
    var STORAGE_KEY = "cookie-consent";
    var banner = document.getElementById("cookie-banner");
    if (!banner) return;

    function getChoice() {
        try { return localStorage.getItem(STORAGE_KEY); } catch (e) { return null; }
    }

    function setChoice(choice) {
        try { localStorage.setItem(STORAGE_KEY, choice); } catch (e) {}
    }

    function applyConsent(choice) {
        var value = choice === "granted" ? "granted" : "denied";
        gtag("consent", "update", {
            ad_storage: value,
            ad_user_data: value,
            ad_personalization: value,
            analytics_storage: value
        });
    }

    // On withdrawal, delete the Google Analytics cookies set earlier. They
    // can sit on this host or its parent domain (e.g. .bestofbart.nl).
    function removeAnalyticsCookies() {
        var host = window.location.hostname;
        var domains = ["", host, "." + host.replace(/^www\./, "")];
        document.cookie.split(";").forEach(function (cookie) {
            var name = cookie.split("=")[0].trim();
            if (!/^(_ga|_gid|_gat)/.test(name)) return;
            domains.forEach(function (domain) {
                document.cookie = name + "=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/" +
                    (domain ? "; domain=" + domain : "");
            });
        });
    }

    function showBanner() {
        banner.hidden = false;
    }

    function hideBanner() {
        banner.hidden = true;
    }

    banner.querySelectorAll("[data-cookie-choice]").forEach(function (button) {
        button.addEventListener("click", function () {
            var choice = button.getAttribute("data-cookie-choice");
            setChoice(choice);
            applyConsent(choice);
            if (choice === "denied") removeAnalyticsCookies();
            hideBanner();
        });
    });

    document.querySelectorAll("[data-cookie-settings]").forEach(function (link) {
        link.addEventListener("click", function () {
            showBanner();
            banner.querySelector("[data-cookie-choice]").focus();
        });
    });

    var stored = getChoice();
    if (stored !== "granted" && stored !== "denied") {
        showBanner();
    }
})();
