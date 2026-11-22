(function () {
    "use strict";

    var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

    // ── Spring ───────────────────────────────────────────────────────────
    // Critically damped (damping ratio 1): settles without overshoot. It
    // starts from whatever value and velocity it is handed, so an animation
    // can be retargeted mid-flight without a jump or a velocity "brick wall".
    // `response` is roughly how quickly it reaches the target, in seconds.
    function animateSpring(options) {
        var from = options.from;
        var to = options.to;
        var v0 = options.velocity || 0;
        var omega = (2 * Math.PI) / (options.response || 0.4);
        var precision = options.precision || 0.001;
        var x0 = from - to;
        var b = v0 + omega * x0;
        var start = null;
        var frame = 0;
        var state = { value: from, velocity: v0 };

        function tick(now) {
            if (start === null) start = now;
            var t = (now - start) / 1000;
            var decay = Math.exp(-omega * t);
            state.value = to + (x0 + b * t) * decay;
            state.velocity = (v0 - omega * b * t) * decay;
            if (Math.abs(state.value - to) < precision && Math.abs(state.velocity) < precision * 10) {
                state.value = to;
                state.velocity = 0;
                options.onUpdate(to);
                if (options.onComplete) options.onComplete();
                return;
            }
            options.onUpdate(state.value);
            frame = requestAnimationFrame(tick);
        }

        frame = requestAnimationFrame(tick);
        state.stop = function () { cancelAnimationFrame(frame); };
        return state;
    }

    // ── Lesson dialog ────────────────────────────────────────────────────
    var dialog = document.getElementById("lessonDialog");

    if (dialog) {
        var panel = dialog.querySelector(".popup");
        var tabs = Array.prototype.slice.call(dialog.querySelectorAll('[role="tab"]'));
        var panels = Array.prototype.slice.call(dialog.querySelectorAll('[role="tabpanel"]'));
        var media = document.getElementById("popupMedia");
        var image = document.getElementById("popupImage");
        var titleEl = document.getElementById("popupTitle");
        var descriptionEl = document.getElementById("popupDescription");
        var filesEl = document.getElementById("popupFiles");
        var tiktokBtn = document.getElementById("popupTiktok");

        var source = null;          // the card the dialog grew out of
        var currentTab = 0;
        var progress = 0;           // 0 = shrunk onto the card, 1 = fully open
        var progressAnim = null;
        var heightAnim = null;
        var geometry = null;

        var fill = function (card) {
            var url = card.getAttribute("data-tiktok-url");
            var cardImage = card.querySelector("img");
            titleEl.textContent = card.querySelector(".item-title").textContent.trim();
            image.src = cardImage.currentSrc || cardImage.src;
            descriptionEl.textContent = card.getAttribute("data-description") || "";

            if (url) {
                media.href = url;
                tiktokBtn.href = url;
                tiktokBtn.hidden = false;
            } else {
                media.removeAttribute("href");
                tiktokBtn.removeAttribute("href");
                tiktokBtn.hidden = true;
            }

            var files = [];
            try { files = JSON.parse(card.getAttribute("data-files") || "[]"); } catch (e) {}
            filesEl.textContent = "";
            if (!files.length) {
                var empty = document.createElement("p");
                empty.textContent = "Geen bestanden beschikbaar";
                filesEl.appendChild(empty);
            }
            files.forEach(function (file) {
                var link = document.createElement("a");
                link.className = "file-link";
                link.href = file.url;
                link.target = "_blank";
                link.rel = "noopener";
                var name = file.name || file.url.split("/").pop();
                try { name = decodeURIComponent(name); } catch (e) {}
                link.textContent = name;
                filesEl.appendChild(link);
            });
        };

        // Layout offset of `el` inside `ancestor`, ignoring transforms.
        var offsetWithin = function (el, ancestor) {
            var x = 0, y = 0, node = el;
            while (node && node !== ancestor) {
                x += node.offsetLeft;
                y += node.offsetTop;
                node = node.offsetParent;
            }
            return { x: x, y: y };
        };

        // The transform that lays the panel exactly over the card. On the
        // TikTok tab the dialog photo is mapped onto the card photo, so the
        // card visibly grows into the dialog; otherwise the whole panel is.
        var measure = function () {
            var panelX = panel.offsetLeft;
            var panelY = panel.offsetTop;
            var anchor = { x: 0, y: 0, width: panel.offsetWidth };
            var target = source.getBoundingClientRect();

            if (currentTab === 0) {
                var at = offsetWithin(image, panel);
                anchor = { x: at.x, y: at.y - panel.scrollTop, width: image.offsetWidth };
                target = source.querySelector("img").getBoundingClientRect();
            }

            var scale = target.width / anchor.width;
            return {
                x: target.left - panelX - scale * anchor.x,
                y: target.top - panelY - scale * anchor.y,
                scale: scale
            };
        };

        var render = function (p) {
            progress = p;
            var rest = 1 - p;
            if (geometry && !reduceMotion.matches) {
                panel.style.transform = "translate(" + geometry.x * rest + "px, " + geometry.y * rest + "px) scale(" +
                    (1 + (geometry.scale - 1) * rest) + ")";
                panel.style.opacity = Math.min(1, Math.max(0, p / 0.3));
            } else {
                // Reduced motion: a plain cross-fade, no scaling or travel.
                panel.style.transform = "";
                panel.style.opacity = p;
            }
            dialog.style.backgroundColor = "rgba(0, 0, 0, " + (0.45 * p) + ")";
        };

        var animateProgress = function (to, onDone) {
            var from = progress;
            var velocity = 0;
            if (progressAnim) {
                from = progressAnim.value;
                velocity = progressAnim.velocity;
                progressAnim.stop();
            }
            progressAnim = animateSpring({
                from: from, to: to, velocity: velocity, response: 0.4, precision: 0.001,
                onUpdate: render,
                onComplete: function () {
                    progressAnim = null;
                    if (onDone) onDone();
                }
            });
        };

        var dialogContentHeight = function () {
            var style = getComputedStyle(dialog);
            return dialog.clientHeight - parseFloat(style.paddingTop) - parseFloat(style.paddingBottom);
        };

        // Centre the panel for its TikTok-tab height, then keep its top edge
        // fixed: switching tabs only moves the bottom edge, so the tab bar
        // never slides out from under the finger.
        var placePanel = function () {
            var available = dialogContentHeight();
            if (currentTab !== 0) {
                var margin = Math.min(parseFloat(panel.style.marginTop) || 0, Math.max(0, available - 240));
                panel.style.marginTop = margin + "px";
                panel.style.maxHeight = (available - margin) + "px";
                return;
            }
            panel.style.marginTop = "";
            panel.style.maxHeight = "";
            var top = Math.max(0, (available - panel.offsetHeight) / 2);
            panel.style.marginTop = top + "px";
            panel.style.maxHeight = (available - top) + "px";
        };

        var selectTab = function (index, opts) {
            opts = opts || {};
            var animate = opts.animate !== false && dialog.open && !reduceMotion.matches;
            var from = panel.offsetHeight;
            var velocity = 0;
            if (heightAnim) {
                velocity = heightAnim.velocity;
                heightAnim.stop();
                heightAnim = null;
            }

            currentTab = index;
            tabs.forEach(function (tab, n) {
                var on = n === index;
                tab.classList.toggle("active", on);
                tab.setAttribute("aria-selected", on ? "true" : "false");
                tab.tabIndex = on ? 0 : -1;
                panels[n].hidden = !on;
            });
            if (opts.focus) tabs[index].focus();

            panel.style.height = "";
            if (!animate) return;
            var to = panel.offsetHeight;
            if (Math.abs(to - from) < 1) return;
            panel.style.height = from + "px";
            heightAnim = animateSpring({
                from: from, to: to, velocity: velocity, response: 0.3, precision: 0.5,
                onUpdate: function (h) { panel.style.height = h + "px"; },
                onComplete: function () {
                    panel.style.height = "";
                    heightAnim = null;
                }
            });
        };

        var openLesson = function (card) {
            fill(card);
            source = card;
            if (!dialog.open) {
                dialog.showModal();
                document.documentElement.classList.add("dialog-open");
            }
            selectTab(0, { animate: false });
            panel.scrollTop = 0;
            placePanel();
            geometry = measure();
            if (!progressAnim) render(progress);
            animateProgress(1);
        };

        var closeLesson = function () {
            if (!dialog.open) return;
            if (heightAnim) {
                heightAnim.stop();
                heightAnim = null;
            }
            geometry = measure();
            animateProgress(0, function () { dialog.close(); });
        };

        // Runs however the dialog ends up closed (our animation, or the
        // browser closing it directly, e.g. a second Escape in Chrome).
        dialog.addEventListener("close", function () {
            if (progressAnim) {
                progressAnim.stop();
                progressAnim = null;
            }
            progress = 0;
            geometry = null;
            panel.style.transform = "";
            panel.style.opacity = "";
            panel.style.height = "";
            dialog.style.backgroundColor = "";
            document.documentElement.classList.remove("dialog-open");
            if (source) source.focus({ preventScroll: true });
            source = null;
        });

        // Escape: animate closed instead of vanishing.
        dialog.addEventListener("cancel", function (event) {
            event.preventDefault();
            closeLesson();
        });

        // Tapping the dimmed area closes. Both press and release must land on
        // it, so selecting text in the panel and releasing outside doesn't.
        var pressedOnScrim = false;
        dialog.addEventListener("pointerdown", function (event) {
            pressedOnScrim = event.target === dialog;
        });
        dialog.addEventListener("click", function (event) {
            if (pressedOnScrim && event.target === dialog) closeLesson();
            pressedOnScrim = false;
        });

        dialog.querySelector("[data-close]").addEventListener("click", closeLesson);

        tabs.forEach(function (tab, n) {
            tab.addEventListener("click", function () { selectTab(n); });
        });

        dialog.querySelector('[role="tablist"]').addEventListener("keydown", function (event) {
            var next = { ArrowRight: currentTab + 1, ArrowLeft: currentTab - 1, Home: 0, End: tabs.length - 1 }[event.key];
            if (next === undefined) return;
            event.preventDefault();
            selectTab((next + tabs.length) % tabs.length, { focus: true });
        });

        window.addEventListener("resize", function () {
            if (dialog.open && !progressAnim) placePanel();
        });

        document.querySelectorAll(".gallery-item").forEach(function (card) {
            card.addEventListener("click", function () { openLesson(card); });
        });
    }

    // ── Filters ──────────────────────────────────────────────────────────
    var filterButtons = document.querySelectorAll(".filter-btn");

    var applyFilter = function (genre) {
        filterButtons.forEach(function (button) {
            var on = button.getAttribute("data-filter") === genre;
            button.classList.toggle("active", on);
            button.setAttribute("aria-pressed", on ? "true" : "false");
        });
        document.querySelectorAll(".gallery-item").forEach(function (item) {
            item.hidden = genre !== "all" && item.getAttribute("data-genre") !== genre;
        });

        // Keep the choice in the address bar so a refresh or shared link
        // shows the same filter (the server renders it from ?genre=).
        var url = new URL(window.location.href);
        if (genre === "all") url.searchParams.delete("genre");
        else url.searchParams.set("genre", genre);
        history.replaceState(null, "", url);
    };

    filterButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            applyFilter(button.getAttribute("data-filter"));
        });
    });
})();
