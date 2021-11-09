import { visit } from "./bundled/turbo.es2017-esm.js";
// XXX fallback to:  visit = (url) => { document.location = url; };

function follow_link (selector) {
    const sel = document.querySelector(selector);
    if (sel) {
        visit(sel.getAttribute('href'));
    }
}

function keydown(e) {
    // https://www.w3.org/TR/uievents-key/#keys-navigation
    if (e.key == "ArrowRight") return follow_link('link[rel~=next]');
    if (e.key == "ArrowLeft") return follow_link('link[rel~=prev]');
}

document.addEventListener('keydown', keydown);

export { };
