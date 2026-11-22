/* ---------- Pictures on the strengths / weaknesses cards and the company profile cards (20 Nov 2026) ----------
   Each card shows a screenshot of a page it links to (MOVESHOT: page screenshots and cited PDF pages) or a news
   article's lead image (NEWSIMG), never the same picture twice in a group. Card text is not changed. */
(function () {
  const base = typeof MEDIA_BASE !== "undefined" ? MEDIA_BASE : "/media/";
  const shots = typeof MOVESHOT !== "undefined" ? MOVESHOT : {};
  const news = typeof NEWSIMG !== "undefined" ? NEWSIMG : {};
  const byUrl = {}; if (typeof EVID !== "undefined") EVID.forEach(r => { if (r[10] && !byUrl[r[10]]) byUrl[r[10]] = r; });
  const e = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const imgFor = u => shots[u] || (byUrl[u] && news[byUrl[u][0]]) || null;

  function decorate(cards, used, prefer) {
    cards.forEach(card => {
      if (card.querySelector(":scope > .cp-img")) return;
      let links = [...card.querySelectorAll("a[href^='http']")];
      const isPdf = a => /\.pdf($|[?#])/i.test(a.getAttribute("href"));
      links = [...links.filter(a => !isPdf(a)), ...links.filter(isPdf)];   // a web page or article picture before a report page
      if (prefer) links = [...links.filter(prefer), ...links.filter(a => !prefer(a))];
      for (const a of links) {
        const u = a.getAttribute("href"), f = imgFor(u);
        if (!f || used.has(f)) continue;
        // two results reports share a layout: a second report picture of the same page number looks like a repeat
        const pg = isPdf(a) && (/\bp\.?\s*(\d+)/i.exec(a.textContent) || [])[1];
        if (pg && used.has("pdf-page-" + pg)) continue;
        if (pg) used.add("pdf-page-" + pg);
        used.add(f);
        const host = (u.split("/")[2] || "").replace(/^www\./, "");
        const label = a.textContent.replace(/\s+/g, " ").trim().slice(0, 40);
        card.insertAdjacentHTML("afterbegin", `<a class="cp-img" href="${e(u)}" target="_blank" rel="noopener"><img loading="lazy" src="${base}${e(f)}" alt=""><span class="ov-img-src">${e(label ? label + " · " : "")}${e(host)}</span></a>`);
        break;
      }
    });
  }
  const swUsed = new Set();
  decorate([...document.querySelectorAll("#swS .swi, #swW .swi")], swUsed);
  // company profiles: the insurer's own website first, then its releases
  decorate([...document.querySelectorAll("#cogrid .cocard")], new Set(), a => /^website$/i.test(a.textContent.trim()) || /homepage|home page/i.test(a.textContent));
})();
