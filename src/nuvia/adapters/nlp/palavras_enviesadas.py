# biased_words.py
# This file serves as a database of words for bias analysis.
# We use sets instead of lists because existence checking (e.g., 'word' in my_set)
# is much faster and more efficient, especially with large lists.

# Category 1: Language with strong emotional charge, used to create "hype" or fear.
LOADED_LANGUAGE = {
    # Hype (Positive)
    'game-changer', 'revolutionary', 'groundbreaking', 'transformative', 'paradigm-shift',
    'seamless', 'effortless', 'state-of-the-art', 'next-gen', 'unleashed', 'perfect',
    'flawless', 'ultimate', 'magical', 'lightning-fast', 'unmatched', 'unparalleled',
    'superior', 'world-class', 'cutting-edge', 'bleeding-edge', 'streamlined', 'optimized',
    'enhanced', 'supercharged', 'turbocharged', 'robust', 'scalable', 'future-proof',
    'essential', 'must-have', 'powerhouse', 'masterpiece', 'brilliant', 'ingenious',
    'elegant', 'powerful', 'dynamic', 'flexible', 'agile', 'intuitive', 'user-friendly',
    'stunning', 'beautiful', 'incredible', 'amazing', 'astonishing', 'phenomenal', 'epic',
    # FUD (Fear, Uncertainty, Doubt - Negative)
    'catastrophic', 'disastrous', 'flawed', 'obsolete', 'legacy', 'bloated', 'crippled',
    'broken', 'toxic', 'nightmare', 'vulnerable', 'unsustainable', 'trainwreck', 'messy',
    'risky', 'dangerous', 'horrifying', 'terrible', 'awful', 'abysmal', 'clunky', 'buggy',
    'slow', 'sluggish', 'inefficient', 'cumbersome', 'convoluted', 'complex', 'insecure',
    'unstable', 'fragile', 'rigid', 'outdated', 'antiquated', 'prehistoric', 'dying',
    'dead', 'doomed', 'failed', 'problematic', 'challenging', 'limited', 'constrained',
    'bottleneck', 'chaotic', 'unreliable', 'untested', 'unproven', 'abomination'
}

# Category 2: Words that present opinion as fact, leaving no room for nuance.
CERTAINTY_AND_ABSOLUTES = {
    'clearly', 'obviously', 'undoubtedly', 'certainly', 'definitely', 'absolutely',
    'unquestionably', 'undeniably', 'surely', 'naturally', 'inarguably', 'indisputably',
    'factually', 'patently', 'evidently', 'always', 'never', 'every', 'all', 'none',
    'guaranteed', 'proven', 'irrefutably', 'categorically', 'totally', 'completely',
    'entirely', 'wholly', 'fundamentally', 'essentially', 'axiomatically', 'self-evidently',
    'without-fail', 'for-sure', 'positively', 'conclusively', 'finally', 'truly', 'genuinely',
    'literally', 'simply', 'must', 'will', 'cannot', 'impossible', 'only', 'sole', 'unique',
    'definitive', 'final', 'ultimate', 'plain', 'simple', 'crystal-clear', 'straightforward',
    'indisputable', 'unarguable', 'without-question', 'no-doubt', 'of-course', 'positively',
    'unavoidably', 'inescapably', 'assuredly', 'unmistakably', 'explicitly', 'specifically',
    'precisely', 'accurately', 'correctly', 'rightfully', 'justly', 'fairly', 'truly',
    'actually', 'really', 'indeed', 'veritably', 'in-fact', 'in-reality', 'honestly',
    'frankly', 'sincerely', 'blatantly', 'manifestly', 'transparently', 'visibly', 'noticeably',
    'perceptibly', 'demonstrably', 'verifiably', 'empirically', 'logically', 'rationally'
}

# Category 3: Appeal to unspecified sources of authority to add weight to an argument.
APPEAL_TO_VAGUE_AUTHORITY = {
    'experts', 'scientists', 'researchers', 'analysts', 'gurus', 'developers', 'community',
    'market', 'sources', 'insiders', 'evangelists', 'thought-leaders', 'architects',
    'engineers', 'pundits', 'studies', 'reports', 'academics', 'professionals', 'specialists',
    'best-practice', 'industry-standard', 'data', 'metrics', 'research', 'consensus',
    'convention', 'common-knowledge', 'folklore', 'tradition', 'everyone', 'everybody',
    'most', 'many', 'some', 'a-number-of', 'a-few', 'the-establishment', 'the-insiders',
    'the-punditry', 'big-tech', 'startups', 'silicon-valley', 'wall-street', 'venture-capitalists',
    'stakeholders', 'users', 'customers', 'clients', 'players', 'actors', 'figures', 'leaders',
    'pioneers', 'visionaries', 'top-minds', 'brains', 'whizzes', 'mavens', 'connoisseurs',
    'authorities', 'officials', 'representatives', 'white-paper', 'case-study', 'documentation',
    'webinar', 'podcast', 'blog-post', 'article', 'publication', 'journal', 'magazine',
    'review', 'commentary', 'feedback', 'testimony', 'anecdote', 'rumor', 'whispers',
    'chatter', 'talk', 'buzz', 'vibe', 'sentiment', 'feeling', 'general-opinion', 'mainstream-view',
    'popular-belief', 'prevailing-wisdom', 'accepted-truth', 'unwritten-rule', 'common-sense',
    'the-cloud', 'the-internet', 'the-web', 'the-industry', 'the-field', 'the-domain'
}

# Main dictionary grouping all categories for easier import and iteration
BIASED_CATEGORIES = {
    "Loaded Language": {
        "words": LOADED_LANGUAGE,
        "color": "#ff7979",
        "explanation": "This word has a strong positive or negative emotional charge. In tech, it's used to create hype or spread fear without presenting objective data (like benchmarks)."
    },
    "Certainty and Absolutes": {
        "words": CERTAINTY_AND_ABSOLUTES,
        "color": "#ffb142",
        "explanation": "These words present an opinion as an undeniable fact. They are often used to oversimplify complex topics and shut down nuanced discussion about a technology's trade-offs."
    },
    "Appeal to Vague Authority": {
        "words": APPEAL_TO_VAGUE_AUTHORITY,
        "color": "#f6e58d",
        "explanation": "Refers to authoritative-sounding groups or concepts ('experts say...', 'data shows...') without specifying them, attempting to add unearned weight to a claim."
    }
}