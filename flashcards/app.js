const { fsrs, createEmptyCard, Rating, State } = window.FSRS;

const App = {
  flashcardData: null,
  scheduler: null,
  currentCategory: null,
  reviewQueue: [],
  currentIndex: 0,
  sessionStats: { again: 0, hard: 0, good: 0, easy: 0 },
  isRevealed: false,

  async init() {
    this.scheduler = fsrs({
      request_retention: 0.9,
      maximum_interval: 365,
      enable_fuzz: true,
      enable_short_term: true
    });

    await this.loadFlashcardData();
    this.initializeCards();
    this.bindEvents();
    this.updateDashboard();
  },

  async loadFlashcardData() {
    const response = await fetch('mtg_flashcards.json');
    this.flashcardData = await response.json();
  },

  initializeCards() {
    const storedCards = Storage.getCards();
    const categories = ['abilityWords', 'keywordAbilities', 'keywordActions'];

    for (const category of categories) {
      const terms = this.flashcardData[category] || [];
      for (const item of terms) {
        const id = `${category}:${item.term}`;
        if (!storedCards[id]) {
          const card = createEmptyCard();
          storedCards[id] = Storage.cardToStorable(card, id, category, item.term);
        }
      }
    }

    Storage.saveCards(storedCards);
  },

  bindEvents() {
    document.querySelectorAll('.category-btn').forEach(btn => {
      btn.addEventListener('click', () => this.startReview(btn.dataset.category));
    });

    document.getElementById('exit-btn').addEventListener('click', () => this.exitReview());
    document.getElementById('back-btn').addEventListener('click', () => this.showDashboard());
    document.getElementById('reset-btn').addEventListener('click', () => this.resetProgress());

    document.getElementById('flashcard').addEventListener('click', () => this.revealCard());

    document.querySelectorAll('.rating-btn').forEach(btn => {
      btn.addEventListener('click', () => this.rateCard(parseInt(btn.dataset.rating)));
    });

    document.addEventListener('keydown', (e) => this.handleKeypress(e));
  },

  handleKeypress(e) {
    if (document.getElementById('review').classList.contains('hidden')) return;

    if (e.code === 'Space' || e.code === 'Enter') {
      e.preventDefault();
      if (!this.isRevealed) {
        this.revealCard();
      }
    } else if (e.code === 'Digit1' || e.code === 'Numpad1') {
      if (this.isRevealed) this.rateCard(Rating.Again);
    } else if (e.code === 'Digit2' || e.code === 'Numpad2') {
      if (this.isRevealed) this.rateCard(Rating.Hard);
    } else if (e.code === 'Digit3' || e.code === 'Numpad3') {
      if (this.isRevealed) this.rateCard(Rating.Good);
    } else if (e.code === 'Digit4' || e.code === 'Numpad4') {
      if (this.isRevealed) this.rateCard(Rating.Easy);
    } else if (e.code === 'Escape') {
      this.exitReview();
    }
  },

  updateDashboard() {
    const storedCards = Storage.getCards();
    const now = new Date();
    let dueCount = 0;
    let newCount = 0;
    const categoryCounts = {
      abilityWords: { total: 0, due: 0 },
      keywordAbilities: { total: 0, due: 0 },
      keywordActions: { total: 0, due: 0 }
    };

    for (const id in storedCards) {
      const stored = storedCards[id];
      const card = Storage.storableToCard(stored);
      const isDue = card.due <= now;
      const isNew = card.state === State.New;

      if (categoryCounts[stored.category]) {
        categoryCounts[stored.category].total++;
        if (isDue) {
          categoryCounts[stored.category].due++;
        }
      }

      if (isDue) dueCount++;
      if (isNew) newCount++;
    }

    document.getElementById('due-count').textContent = dueCount;
    document.getElementById('new-count').textContent = newCount;
    document.getElementById('total-reviews').textContent = Storage.getStats().totalReviews;

    for (const category in categoryCounts) {
      const el = document.getElementById(`count-${category}`);
      if (el) {
        const { total, due } = categoryCounts[category];
        el.textContent = due > 0 ? `${due} due / ${total} total` : `${total} cards`;
      }
    }
  },

  startReview(category) {
    this.currentCategory = category;
    this.sessionStats = { again: 0, hard: 0, good: 0, easy: 0 };
    this.buildReviewQueue();

    if (this.reviewQueue.length === 0) {
      alert('No cards to review in this category!');
      return;
    }

    this.currentIndex = 0;
    this.showView('review');
    this.showCard();
  },

  buildReviewQueue() {
    const storedCards = Storage.getCards();
    const now = new Date();
    const queue = [];

    for (const id in storedCards) {
      const stored = storedCards[id];
      if (stored.category !== this.currentCategory) continue;

      const card = Storage.storableToCard(stored);
      if (card.due <= now) {
        queue.push({
          id,
          stored,
          card,
          term: stored.term,
          definition: this.getDefinition(stored.category, stored.term)
        });
      }
    }

    queue.sort((a, b) => {
      const stateOrder = { [State.Learning]: 0, [State.Relearning]: 1, [State.Review]: 2, [State.New]: 3 };
      return (stateOrder[a.card.state] || 4) - (stateOrder[b.card.state] || 4);
    });

    this.reviewQueue = queue;
  },

  getDefinition(category, term) {
    const items = this.flashcardData[category] || [];
    const item = items.find(i => i.term === term);
    return item ? item.definition : '';
  },

  showCard() {
    if (this.currentIndex >= this.reviewQueue.length) {
      this.showComplete();
      return;
    }

    const item = this.reviewQueue[this.currentIndex];
    this.isRevealed = false;

    document.getElementById('progress').textContent =
      `${this.currentIndex + 1} / ${this.reviewQueue.length}`;

    const categoryLabels = {
      abilityWords: 'Ability Word',
      keywordAbilities: 'Keyword Ability',
      keywordActions: 'Keyword Action'
    };

    document.getElementById('card-category').textContent = categoryLabels[item.stored.category] || '';
    document.getElementById('card-term').textContent = item.term;
    document.getElementById('card-definition').textContent = item.definition;
    document.getElementById('card-definition').classList.add('hidden');
    document.getElementById('card-hint').classList.remove('hidden');
    document.getElementById('rating-buttons').classList.add('hidden');

    this.updateIntervalPreviews(item.card);
  },

  revealCard() {
    if (this.isRevealed) return;
    this.isRevealed = true;

    document.getElementById('card-definition').classList.remove('hidden');
    document.getElementById('card-hint').classList.add('hidden');
    document.getElementById('rating-buttons').classList.remove('hidden');
  },

  updateIntervalPreviews(card) {
    const now = new Date();
    const ratings = [Rating.Again, Rating.Hard, Rating.Good, Rating.Easy];
    const ids = ['interval-again', 'interval-hard', 'interval-good', 'interval-easy'];

    for (let i = 0; i < ratings.length; i++) {
      const result = this.scheduler.next(card, now, ratings[i]);
      const interval = this.formatInterval(result.card);
      document.getElementById(ids[i]).textContent = interval;
    }
  },

  formatInterval(card) {
    const now = new Date();
    const due = card.due;
    const diffMs = due - now;
    const diffMins = Math.round(diffMs / 60000);
    const diffHours = Math.round(diffMs / 3600000);
    const diffDays = Math.round(diffMs / 86400000);

    if (diffMins < 1) return '<1m';
    if (diffMins < 60) return `${diffMins}m`;
    if (diffHours < 24) return `${diffHours}h`;
    return `${diffDays}d`;
  },

  rateCard(rating) {
    if (!this.isRevealed) return;

    const item = this.reviewQueue[this.currentIndex];
    const now = new Date();
    const result = this.scheduler.next(item.card, now, rating);

    const storedCard = Storage.cardToStorable(
      result.card,
      item.id,
      item.stored.category,
      item.term
    );
    Storage.saveCard(item.id, storedCard);

    const storedLog = Storage.logToStorable(result.log, item.id);
    Storage.addLog(storedLog);

    Storage.incrementReviews();

    switch (rating) {
      case Rating.Again: this.sessionStats.again++; break;
      case Rating.Hard: this.sessionStats.hard++; break;
      case Rating.Good: this.sessionStats.good++; break;
      case Rating.Easy: this.sessionStats.easy++; break;
    }

    this.currentIndex++;
    this.showCard();
  },

  showComplete() {
    const total = this.sessionStats.again + this.sessionStats.hard +
                  this.sessionStats.good + this.sessionStats.easy;

    document.getElementById('session-reviewed').textContent = total;
    document.getElementById('session-again').textContent = this.sessionStats.again;
    document.getElementById('session-hard').textContent = this.sessionStats.hard;
    document.getElementById('session-good').textContent = this.sessionStats.good;
    document.getElementById('session-easy').textContent = this.sessionStats.easy;

    this.showView('complete');
  },

  exitReview() {
    this.showDashboard();
  },

  showDashboard() {
    this.updateDashboard();
    this.showView('dashboard');
  },

  showView(viewId) {
    document.querySelectorAll('.view').forEach(v => v.classList.add('hidden'));
    document.getElementById(viewId).classList.remove('hidden');
  },

  resetProgress() {
    if (confirm('Are you sure you want to reset all progress? This cannot be undone.')) {
      Storage.clearAll();
      this.initializeCards();
      this.updateDashboard();
    }
  }
};

document.addEventListener('DOMContentLoaded', () => App.init());
