/* ---------- Review-call feedback, 20 Nov 2026 ----------
   1. Charts and data first: on every tab the picture galleries (live captures, news in pictures, ads and posts,
      website screenshots) move below the charts and tables, under "Supporting screenshots and sources".
   2. Progressive disclosure everywhere: long paragraphs show their first lines with "See more"; long bullet lists
      show the first items with "Show N more". The text itself is unchanged.
   3. Platform filter: choosing Xiaohongshu or WeChat opens the mainland social section filtered to that platform
      (those posts are search-based, so they are not mixed into the activity counts). */
(function () {
  const q = (s, r = document) => r.querySelector(s), qa = (s, r = document) => [...r.querySelectorAll(s)];

  // ---- 1. galleries below the data
  const GAL = qa("#captures, #news-pics, #news-pics-p2, main section.view .vg");
  const bySec = new Map();
  GAL.forEach(el => { const sec = el.closest("section.view"); if (!sec || el.closest(".sup-wrap")) return; (bySec.get(sec) || bySec.set(sec, []).get(sec)).push(el); });
  bySec.forEach((els, sec) => {
    const h = document.createElement("h3"); h.className = "sup-h"; h.textContent = "Supporting screenshots and sources";
    const wrap = document.createElement("div"); wrap.className = "sup-wrap";
    wrap.append(h, ...els); sec.appendChild(wrap);
  });

  // ---- 2. progressive disclosure for long text
  const SKIP = ".pd-hide, .ob-hero, .mc, p.muted.small, table, .insight, #insights, .ds-content, .nw-card, .ov-card, .cn-card, #evFocus, .ckey, .geo-card, nav, .fbar, .op-meta, .sec-head, .fx, .pd-clamp, .script, details:not([open]) > *, .sup-wrap";
  const clampP = p => {
    if (p.dataset.pd2 || p.closest(SKIP) || p.textContent.trim().length < 300 || p.querySelector("button, input, select")) return;
    p.dataset.pd2 = "1"; p.classList.add("pd-clamp2");
    const b = document.createElement("button"); b.type = "button"; b.className = "pd-more pd-see"; b.textContent = "See more";
    p.insertAdjacentElement("afterend", b);
    b.addEventListener("click", () => { const open = p.classList.toggle("pd-clamp2") === false; b.textContent = open ? "See less" : "See more"; });
  };
  const clampList = ul => {
    if (ul.dataset.pd2 || ul.closest(SKIP) || ul.closest("#topPosts") || ul.id === "topPosts") return;
    const items = [...ul.children].filter(x => x.tagName === "LI"); if (items.length <= 5) return;
    ul.dataset.pd2 = "1"; const keep = 4;
    items.slice(keep).forEach(li => li.classList.add("pd-li-hide"));
    const b = document.createElement("button"); b.type = "button"; b.className = "pd-more pd-see"; b.textContent = `Show ${items.length - keep} more`;
    ul.insertAdjacentElement("afterend", b);
    b.addEventListener("click", () => { const open = !items[keep].classList.contains("pd-li-hide");
      items.slice(keep).forEach(li => li.classList.toggle("pd-li-hide", open)); b.textContent = open ? `Show ${items.length - keep} more` : "Show fewer"; });
  };
  const run = () => { qa("main section.view p").forEach(clampP); qa("main section.view ul, main section.view ol").forEach(clampList); };
  run();
  let t = null;
  document.addEventListener("click", e => { if (e.target.closest("nav a, [data-view]")) { clearTimeout(t); t = setTimeout(run, 400); } });

  // ---- 1b. evidence page: the Back bar stays pinned while scrolling the whole page (it was inside the short focus box)
  const evSec = q("#ev"), evF = q("#evFocus");
  if (evSec && evF) {
    const hold = document.createElement("div"); hold.id = "evBarHold"; evSec.prepend(hold);
    const sync = () => { const bar = evF.querySelector(".ev-bar");
      if (bar) { hold.replaceChildren(bar); } else if (evF.hidden || !evF.innerHTML.trim()) hold.replaceChildren(); };
    new MutationObserver(sync).observe(evF, { childList: true, subtree: true, attributes: true, attributeFilter: ["hidden"] });
    sync();
  }

  // ---- 3. Xiaohongshu / WeChat in the platform filter
  document.addEventListener("change", e => {
    const s = e.target; if (s.id !== "fPlat") return;
    const o = s.selectedOptions[0]; if (!o || !o.dataset.cn) { s.dataset.prev = s.value; return; }
    e.stopImmediatePropagation();
    const plat = o.value; s.value = s.dataset.prev || "all";
    const nav = q('nav.toc a[data-view="deep"]'); if (nav) nav.click();
    setTimeout(() => { const sec = q("#cnsoc"); if (!sec) return;
      qa(".cn-p-f button", sec).find(b => b.dataset.p === plat)?.click();
      sec.scrollIntoView({ behavior: "smooth", block: "start" });
      if (!q("#cnNote", sec)) sec.querySelector("h3")?.insertAdjacentHTML("afterend", `<p class="small" id="cnNote" style="border-left:3px solid var(--x-red);padding:6px 10px">Showing ${plat} posts. Xiaohongshu and WeChat posts are found by searching each insurer's name, so they have their own section and are not added to the activity counts in the other charts.</p>`); }, 350);
  }, true);
})();
