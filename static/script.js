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
    if (e.key == "ArrowDown") return follow_link('fragment-link[rel~=next]');
    if (e.key == "ArrowUp") return follow_link('fragment-link[rel~=prev]');
    if (e.key == " ") return follow_link('seq-link[rel~=next]');
    if (e.key == "Backspace") return follow_link('seq-link[rel~=prev]');
    if (e.key == "Home") return follow_link('fraglim-link[rel~=prev]');
    if (e.key == "End") return follow_link('fraglim-link[rel~=next]');
}

document.addEventListener('keydown', keydown);

export { };
