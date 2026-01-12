const STORAGE_KEYS = {
  CARDS: 'mtg-flashcards-cards',
  LOGS: 'mtg-flashcards-logs',
  STATS: 'mtg-flashcards-stats'
};

const Storage = {
  getCards() {
    const data = localStorage.getItem(STORAGE_KEYS.CARDS);
    return data ? JSON.parse(data) : {};
  },

  saveCards(cards) {
    localStorage.setItem(STORAGE_KEYS.CARDS, JSON.stringify(cards));
  },

  getCard(id) {
    const cards = this.getCards();
    return cards[id] || null;
  },

  saveCard(id, card) {
    const cards = this.getCards();
    cards[id] = card;
    this.saveCards(cards);
  },

  getLogs() {
    const data = localStorage.getItem(STORAGE_KEYS.LOGS);
    return data ? JSON.parse(data) : [];
  },

  addLog(log) {
    const logs = this.getLogs();
    logs.push(log);
    localStorage.setItem(STORAGE_KEYS.LOGS, JSON.stringify(logs));
  },

  getStats() {
    const data = localStorage.getItem(STORAGE_KEYS.STATS);
    return data ? JSON.parse(data) : {
      totalReviews: 0,
      lastReviewDate: null
    };
  },

  saveStats(stats) {
    localStorage.setItem(STORAGE_KEYS.STATS, JSON.stringify(stats));
  },

  incrementReviews() {
    const stats = this.getStats();
    stats.totalReviews++;
    stats.lastReviewDate = new Date().toISOString();
    this.saveStats(stats);
    return stats;
  },

  clearAll() {
    localStorage.removeItem(STORAGE_KEYS.CARDS);
    localStorage.removeItem(STORAGE_KEYS.LOGS);
    localStorage.removeItem(STORAGE_KEYS.STATS);
  },

  cardToStorable(card, id, category, term) {
    return {
      id,
      category,
      term,
      due: card.due.toISOString(),
      stability: card.stability,
      difficulty: card.difficulty,
      elapsed_days: card.elapsed_days,
      scheduled_days: card.scheduled_days,
      learning_steps: card.learning_steps,
      reps: card.reps,
      lapses: card.lapses,
      state: card.state,
      last_review: card.last_review ? card.last_review.toISOString() : null
    };
  },

  storableToCard(stored) {
    return {
      due: new Date(stored.due),
      stability: stored.stability,
      difficulty: stored.difficulty,
      elapsed_days: stored.elapsed_days,
      scheduled_days: stored.scheduled_days,
      learning_steps: stored.learning_steps,
      reps: stored.reps,
      lapses: stored.lapses,
      state: stored.state,
      last_review: stored.last_review ? new Date(stored.last_review) : null
    };
  },

  logToStorable(log, id) {
    return {
      id,
      rating: log.rating,
      state: log.state,
      due: log.due.toISOString(),
      stability: log.stability,
      difficulty: log.difficulty,
      elapsed_days: log.elapsed_days,
      last_elapsed_days: log.last_elapsed_days,
      scheduled_days: log.scheduled_days,
      learning_steps: log.learning_steps,
      review: log.review.toISOString()
    };
  }
};
