/**
 * Card Detail View - renders full card information page.
 *
 * Depends on globals from index.html: api(), formatPrice(), renderSetCode(),
 * cardDataMap, switchTab(), loadDeck(), copyToClipboard(), showCardRaw()
 */

// Navigation history for back button
let cardDetailHistory = [];

async function showCardDetail(uuid) {
    const mainContent = document.getElementById('mainContent');
    mainContent.innerHTML = '<div class="loading">Loading card...</div>';

    try {
        const card = await api(`/cards/${uuid}`);
        cardDataMap[card.uuid] = card;
        cardDetailHistory.push(uuid);
        renderCardDetailView(card);
    } catch (error) {
        mainContent.innerHTML = '<div class="loading">Error loading card</div>';
    }
}

function renderCardDetailView(card) {
    const mainContent = document.getElementById('mainContent');

    const imageUrl = card.image_url;
    const manaCostHtml = renderManaCostIcons(card.mana_cost);
    const statsRow = buildStatsRow(card);
    const oracleHtml = card.text ? renderOracleText(card.text) : '';
    const flavorHtml = card.flavor_text
        ? `<div class="card-detail-flavor">${escapeHtml(card.flavor_text)}</div>` : '';
    const legalitiesHtml = renderLegalities(card.legalities);
    const pricesHtml = renderAllPrices(card.all_prices);
    const metaHtml = renderMetaGrid(card);
    const keywordsHtml = renderKeywords(card.keywords);
    const printingsHtml = renderOtherPrintings(card.other_printings);
    const decksHtml = renderDeckAppearances(card.appears_in_decks);
    const collectionHtml = renderCollectionStatus(card);

    mainContent.innerHTML = `
        <div class="card-detail-back" onclick="goBackFromCard()">&#8592; Back</div>
        <div class="card-detail-layout">
            <div class="card-detail-left">
                ${imageUrl
                    ? `<img src="${imageUrl}" alt="${escapeHtml(card.name)}" onerror="this.style.display='none'">`
                    : '<div class="card-image-placeholder" style="height:440px;display:flex;align-items:center;justify-content:center;background:#16213e;border-radius:12px;">No image</div>'
                }
                ${collectionHtml}
            </div>
            <div class="card-detail-right">
                <div class="card-detail-header">
                    <h2>
                        ${escapeHtml(card.name)}
                        <span class="card-detail-mana-cost">${manaCostHtml}</span>
                    </h2>
                    <div class="card-detail-type-line">${escapeHtml(card.type || '')}</div>
                    ${statsRow}
                </div>

                ${oracleHtml ? `
                    <div class="card-detail-section">
                        <h3>Oracle Text</h3>
                        <div class="card-detail-oracle">${oracleHtml}</div>
                        ${flavorHtml}
                    </div>
                ` : ''}

                ${keywordsHtml}
                ${metaHtml}
                ${legalitiesHtml}
                ${pricesHtml}
                ${printingsHtml}
                ${decksHtml}

                <div style="margin-top:12px;font-size:0.75rem;color:#555;">
                    UUID: ${card.uuid}
                    <span style="cursor:pointer;color:#888;margin-left:8px;" onclick="copyToClipboard('${card.uuid}')">Copy</span>
                    <span style="cursor:pointer;color:#888;margin-left:8px;" onclick="showCardRaw('${card.uuid}')">raw</span>
                </div>
            </div>
        </div>
    `;
}

function goBackFromCard() {
    cardDetailHistory.pop(); // remove current
    if (cardDetailHistory.length > 0) {
        const prevUuid = cardDetailHistory.pop(); // will be re-pushed by showCardDetail
        showCardDetail(prevUuid);
    } else {
        // Go back to whatever tab is active
        const activeTab = document.querySelector('.tab-btn.active');
        if (activeTab) activeTab.click();
    }
}

function renderManaCostIcons(manaCost) {
    if (!manaCost) return '';
    // Parse {W}, {U}, {B}, {R}, {G}, {C}, {1}, {2}, etc.
    return manaCost.replace(/\{([^}]+)\}/g, (_, symbol) => {
        const s = symbol.toLowerCase().replace('/', '');
        return `<i class="ms ms-${s} ms-cost ms-shadow"></i>`;
    });
}

function renderOracleText(text) {
    // Escape HTML, then replace mana symbols and newlines
    let html = escapeHtml(text);
    html = html.replace(/\{([^}]+)\}/g, (_, symbol) => {
        const s = symbol.toLowerCase().replace('/', '');
        return `<i class="ms ms-${s} ms-cost ms-shadow" style="font-size:0.85em"></i>`;
    });
    return html;
}

function buildStatsRow(card) {
    const parts = [];
    if (card.power && card.toughness) {
        parts.push(`${card.power}/${card.toughness}`);
    }
    if (card.loyalty) parts.push(`Loyalty: ${card.loyalty}`);
    if (card.defense) parts.push(`Defense: ${card.defense}`);
    if (card.mana_value !== null && card.mana_value !== undefined) {
        parts.push(`MV ${card.mana_value}`);
    }

    if (parts.length === 0) return '';
    return `<div class="card-detail-stats-row">
        ${parts.map(p => `<div class="card-detail-stat">${p}</div>`).join('')}
    </div>`;
}

function renderKeywords(keywords) {
    if (!keywords || keywords.length === 0) return '';
    return `
        <div class="card-detail-section">
            <h3>Keywords</h3>
            <div class="keywords-list">
                ${keywords.map(k => `<span class="keyword-tag">${escapeHtml(k)}</span>`).join('')}
            </div>
        </div>
    `;
}

function renderMetaGrid(card) {
    const items = [];
    const add = (label, value) => { if (value) items.push({ label, value }); };

    add('Set', `<a href="#" onclick="switchTab('sets'); loadSet('${card.set_code}'); return false;" style="color:#4cc9f0;text-decoration:none;cursor:pointer;">${renderSetCode(card.set_code)} ${escapeHtml(card.set_name || card.set_code || '')}</a>`);
    add('Rarity', capitalize(card.rarity));
    add('Number', card.number);
    add('Artist', card.artist);
    add('Layout', capitalize(card.layout));
    add('Frame', card.frame_version);
    add('Border', capitalize(card.border_color));
    if (card.finishes && card.finishes.length) add('Finishes', card.finishes.map(capitalize).join(', '));

    const flags = [];
    if (card.is_reprint) flags.push('Reprint');
    if (card.is_reserved) flags.push('Reserved List');
    if (card.is_promo) flags.push('Promo');
    if (flags.length) add('Flags', flags.join(', '));

    if (items.length === 0) return '';
    return `
        <div class="card-detail-section">
            <h3>Details</h3>
            <div class="card-detail-meta-grid">
                ${items.map(i => `
                    <div class="card-detail-meta-item">
                        <span class="label">${i.label}</span>
                        <span class="value">${i.value}</span>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function renderLegalities(legalities) {
    if (!legalities || Object.keys(legalities).length === 0) return '';

    // Sort: legal first, then by format name
    const sorted = Object.entries(legalities).sort((a, b) => {
        const order = { 'Legal': 0, 'Restricted': 1, 'Banned': 2, 'Not Legal': 3 };
        const diff = (order[a[1]] ?? 3) - (order[b[1]] ?? 3);
        return diff !== 0 ? diff : a[0].localeCompare(b[0]);
    });

    return `
        <div class="card-detail-section">
            <h3>Legalities</h3>
            <div class="legalities-grid">
                ${sorted.map(([format, status]) => {
                    const cls = status.toLowerCase().replace(/\s+/g, '-');
                    return `
                        <div class="legality-item">
                            <span class="format-name">${format}</span>
                            <span class="legality-badge ${cls}">${status}</span>
                        </div>
                    `;
                }).join('')}
            </div>
        </div>
    `;
}

function renderAllPrices(prices) {
    if (!prices || prices.length === 0) return '';

    // Group by provider
    const grouped = {};
    for (const p of prices) {
        if (!grouped[p.provider]) grouped[p.provider] = [];
        grouped[p.provider].push(p);
    }

    return `
        <div class="card-detail-section">
            <h3>Prices</h3>
            <table class="prices-table">
                <thead>
                    <tr><th>Provider</th><th>Finish</th><th>Type</th><th style="text-align:right">Price</th></tr>
                </thead>
                <tbody>
                    ${prices.map(p => `
                        <tr>
                            <td>${escapeHtml(p.provider)}</td>
                            <td>${capitalize(p.finish)}</td>
                            <td>${capitalize(p.listing_type)}</td>
                            <td>$${p.price.toFixed(2)}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

function renderOtherPrintings(printings) {
    if (!printings || printings.length === 0) return '';
    return `
        <div class="card-detail-section">
            <h3>Other Printings (${printings.length})</h3>
            <div class="printings-row">
                ${printings.map(p => `
                    <div class="printing-thumb" onclick="showCardDetail('${p.uuid}')">
                        ${p.image_url
                            ? `<img src="${p.image_url}" alt="${escapeHtml(p.set_name)}" loading="lazy" onerror="this.style.display='none'">`
                            : `<div style="height:140px;background:#16213e;border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:0.7rem;color:#555;">No img</div>`
                        }
                        <div class="printing-label">
                            ${renderSetCode(p.set_code)} ${p.set_code}
                            ${p.owns ? '<span class="owned-indicator">&#10003;</span>' : ''}
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function renderDeckAppearances(decks) {
    if (!decks || decks.length === 0) return '';
    return `
        <div class="card-detail-section">
            <h3>Appears in ${decks.length} Deck${decks.length !== 1 ? 's' : ''}</h3>
            <div style="max-height:200px;overflow-y:auto;">
                ${decks.map(d => `
                    <div class="deck-item" onclick="loadDeck('${d.file}'); switchTab('decks');" style="padding:6px 10px;">
                        <div class="deck-name" style="font-size:0.9rem;">${escapeHtml(d.name)}</div>
                        <div class="deck-code" style="font-size:0.75rem;">x${d.count}</div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function renderCollectionStatus(card) {
    if (!card.owns && !card.wants) {
        return `<div style="margin-top:12px;text-align:center;">
            <button class="raw-btn" style="padding:8px 16px;font-size:0.9rem;" onclick="addToCollection('${card.uuid}')">
                Add to Collection
            </button>
        </div>`;
    }

    const c = card.collection || {};
    return `<div style="margin-top:12px;background:#16213e;padding:12px;border-radius:8px;">
        <div style="font-size:0.8rem;color:#888;text-transform:uppercase;margin-bottom:8px;">Collection</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;font-size:0.85rem;">
            <div>Owned: <strong>${c.quantity_owned || 0}</strong></div>
            <div>Foil: <strong>${c.quantity_owned_foil || 0}</strong></div>
            <div>Wanted: <strong>${c.quantity_wanted || 0}</strong></div>
            <div>Wanted Foil: <strong>${c.quantity_wanted_foil || 0}</strong></div>
        </div>
        ${c.condition ? `<div style="margin-top:6px;font-size:0.8rem;color:#aaa;">Condition: ${c.condition}</div>` : ''}
        ${c.notes ? `<div style="margin-top:4px;font-size:0.8rem;color:#aaa;">Notes: ${escapeHtml(c.notes)}</div>` : ''}
    </div>`;
}

async function addToCollection(uuid) {
    try {
        await api(`/cards/${uuid}/collection`, {}, 'POST');
        showCardDetail(uuid); // refresh
    } catch (e) {
        // silently fail
    }
}

// Utility helpers
function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function capitalize(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
}
