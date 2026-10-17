/**
 * SahakarSeva Full-Page Multilingual Engine powered by Google Translator API
 * Seamless bidirectional translation: English <-> Marathi <-> Hindi
 * Guarantees 100% loss-free, instantaneous restoration when switching back to English
 * and seamless cross-translation between Marathi and Hindi without any DOM corruption.
 */

(function () {
    'use strict';

    // ─── 0. PURGE OLD GOOGLE TRANSLATE WIDGET COOKIES ─────────────────────────
    function purgeGoogTransCookies() {
        try {
            const host = window.location.hostname;
            const domains = ['', host, '.' + host];
            const paths = ['/', window.location.pathname];
            domains.forEach(d => {
                paths.forEach(p => {
                    document.cookie = `googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=${p};` + (d ? ` domain=${d};` : '');
                });
            });
        } catch (e) {}
    }
    purgeGoogTransCookies();

    // ─── 1. FAST NAVIGATION & CORE LABELS DICTIONARY ──────────────────────────
    const FAST_NAV = {
        en: {
            current_label: "English",
            nav_fed_command: "Home",
            nav_aff_societies: "Societies",
            nav_soc_onboarding: "Approvals",
            nav_disputes: "Complaints",
            nav_finance: "Money",
            nav_circulars: "Announcements",
            nav_audit: "Security",
            nav_gov_settings: "Settings",
            nav_soc_dashboard: "Home",
            nav_service_tickets: "Bookings",
            nav_workers: "Workers",
            nav_customers: "Customers",
            nav_attendance: "Attendance",
            nav_invoices: "Payments",
            nav_supplies: "Supplies",
            nav_community_orders: "Projects",
            nav_ai_demand: "AI & Demand",
            nav_reports: "Reports",
            nav_analytics: "Reports",
            nav_settings: "Settings",
            nav_member_dashboard: "Home",
            nav_todays_jobs: "My Jobs",
            nav_assigned_tickets: "My Jobs",
            nav_gps_checkin: "Attendance",
            nav_timesheets: "Work Hours",
            nav_expense_claims: "Expenses",
            nav_earnings: "Earnings",
            nav_certifications: "Certificates",
            nav_safety_reports: "Safety",
            nav_messages: "Messages",
            nav_welfare_profile: "Profile",
            nav_client_hub: "Home",
            nav_societies: "Societies",
            nav_book_service: "Book Service",
            nav_my_bookings: "My Bookings",
            nav_client_invoices: "Payments",
            nav_support: "Help",
            nav_profile: "Profile"
        },
        hi: {
            current_label: "हिंदी",
            nav_fed_command: "होम",
            nav_aff_societies: "सहकारी",
            nav_soc_onboarding: "मंजूरी",
            nav_disputes: "शिकायतें",
            nav_finance: "पैसे",
            nav_circulars: "सूचनाएँ",
            nav_audit: "सुरक्षा",
            nav_gov_settings: "सेटिंग्स",
            nav_soc_dashboard: "होम",
            nav_service_tickets: "बुकिंग",
            nav_workers: "श्रमिक",
            nav_customers: "ग्राहक",
            nav_attendance: "हाजिरी",
            nav_invoices: "भुगतान",
            nav_supplies: "सामग्री",
            nav_community_orders: "काम",
            nav_ai_demand: "AI और मांग",
            nav_reports: "रिपोर्ट",
            nav_analytics: "रिपोर्ट",
            nav_settings: "सेटिंग्स",
            nav_member_dashboard: "होम",
            nav_todays_jobs: "मेरे काम",
            nav_assigned_tickets: "मेरे काम",
            nav_gps_checkin: "हाजिरी",
            nav_timesheets: "काम के घंटे",
            nav_expense_claims: "खर्च",
            nav_earnings: "कमाई",
            nav_certifications: "प्रमाणपत्र",
            nav_safety_reports: "सुरक्षा",
            nav_messages: "संदेश",
            nav_welfare_profile: "प्रोफाइल",
            nav_client_hub: "होम",
            nav_societies: "सहकारी",
            nav_book_service: "सेवा बुक करें",
            nav_my_bookings: "मेरी बुकिंग",
            nav_client_invoices: "भुगतान",
            nav_support: "मदद",
            nav_profile: "प्रोफाइल"
        },
        mr: {
            current_label: "मराठी",
            nav_fed_command: "होम",
            nav_aff_societies: "सहकारी",
            nav_soc_onboarding: "मंजुरी",
            nav_disputes: "तक्रारी",
            nav_finance: "पैसे",
            nav_circulars: "सूचना",
            nav_audit: "सुरक्षा",
            nav_gov_settings: "सेटिंग्ज",
            nav_soc_dashboard: "होम",
            nav_service_tickets: "बुकिंग",
            nav_workers: "कामगार",
            nav_customers: "ग्राहक",
            nav_attendance: "हजेरी",
            nav_invoices: "पेमेंट",
            nav_supplies: "साहित्य",
            nav_community_orders: "काम",
            nav_ai_demand: "AI आणि मागणी",
            nav_reports: "अहवाल",
            nav_analytics: "अहवाल",
            nav_settings: "सेटिंग्ज",
            nav_member_dashboard: "होम",
            nav_todays_jobs: "माझी कामे",
            nav_assigned_tickets: "माझी कामे",
            nav_gps_checkin: "हजेरी",
            nav_timesheets: "कामाचे तास",
            nav_expense_claims: "खर्च",
            nav_earnings: "कमाई",
            nav_certifications: "प्रमाणपत्रे",
            nav_safety_reports: "सुरक्षा",
            nav_messages: "संदेश",
            nav_welfare_profile: "प्रोफाइल",
            nav_client_hub: "होम",
            nav_societies: "सहकारी",
            nav_book_service: "सेवा बुक करा",
            nav_my_bookings: "माझ्या बुकिंग",
            nav_client_invoices: "पेमेंट",
            nav_support: "मदत",
            nav_profile: "प्रोफाइल"
        }
    };

    // Instant local status keywords
    const CORE_KEYWORDS = {
        "Status": { hi: "स्थिति", mr: "स्थिती" },
        "Actions": { hi: "कार्रवाई", mr: "कृती" },
        "Cancel": { hi: "रद्द करें", mr: "रद्द करा" },
        "Save Changes": { hi: "बदलाव सहेजें", mr: "बदल जतन करा" },
        "Close": { hi: "बंद करें", mr: "बंद करा" },
        "Confirm": { hi: "पुष्टि करें", mr: "खात्री करा" },
        "Book Service": { hi: "सेवा बुक करें", mr: "सेवा बुक करा" },
        "My Bookings": { hi: "मेरी बुकिंग", mr: "माझ्या बुकिंग" },
        "Payments": { hi: "भुगतान", mr: "पेमेंट" },
        "Attendance": { hi: "उपस्थिति", mr: "हजेरी" },
        "Earnings": { hi: "कमाई", mr: "कमाई" },
        "Benefits": { hi: "लाभ", mr: "फायदे" },
        "Book Now": { hi: "अभी बुक करें", mr: "आत्ताच बुक करा" },
        "Add Worker": { hi: "श्रमिक जोड़ें", mr: "कामगार जोडा" },
        "Download PDF Report": { hi: "पीडीएफ रिपोर्ट डाउनलोड करें", mr: "पीडीएफ अहवाल डाउनलोड करा" },
        "Export CSV": { hi: "सीएसवी निर्यात करें", mr: "सीएसव्ही निर्यात करा" },
        "Refresh": { hi: "ताज़ा करें", mr: "रिफ्रेश करा" },
        "Sign In": { hi: "साइन इन करें", mr: "साइन इन करा" },
        "Sign Out": { hi: "लॉग आउट", mr: "लॉग आऊट" },
        "Logout": { hi: "लॉग आउट", mr: "लॉग आऊट" },
        "Pending": { hi: "लंबित", mr: "प्रलंबित" },
        "Active": { hi: "सक्रिय", mr: "सक्रिय" },
        "Completed": { hi: "पूर्ण", mr: "पूर्ण झाले" },
        "In Progress": { hi: "प्रगति पर", mr: "प्रगतीपथावर" },
        "Rejected": { hi: "अस्वीकृत", mr: "नाकारले" },
        "Approved": { hi: "स्वीकृत", mr: "मंजूर" },
        "Verified": { hi: "सत्यापित", mr: "पडताळणी झालेले" }
    };

    // ─── 2. PRISTINE ENGLISH BASELINE REPOSITORY ──────────────────────────────
    // WeakMap guarantees pristine original English text is NEVER lost, even after 100 language changes
    const ORIGINAL_TEXTS = new WeakMap();
    const TRACKED_TEXT_NODES = new Set();
    const TRACKED_INPUTS = new Set();
    const TRACKED_BUTTONS = new Set();
    const TRACKED_TITLES = new Set();

    // Cache for API responses
    const memoryCache = {};

    function getCache(lang, text) {
        const key = `${lang}:${text}`;
        if (memoryCache[key]) return memoryCache[key];
        try {
            const val = sessionStorage.getItem('gt_' + key);
            if (val) {
                memoryCache[key] = val;
                return val;
            }
        } catch (e) {}
        return null;
    }

    function setCache(lang, text, translated) {
        const key = `${lang}:${text}`;
        memoryCache[key] = translated;
        try {
            sessionStorage.setItem('gt_' + key, translated);
        } catch (e) {}
    }

    // Capture English originals for a DOM subtree
    function captureOriginals(rootNode) {
        if (!rootNode) rootNode = document.body;
        const ignoredTags = new Set(['SCRIPT', 'STYLE', 'CODE', 'PRE', 'SVG', 'PATH']);

        const walker = document.createTreeWalker(
            rootNode,
            NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT,
            {
                acceptNode: function (node) {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        if (ignoredTags.has(node.tagName) || 
                            (node.classList && (node.classList.contains('no-translate') || node.classList.contains('notranslate'))) ||
                            node.id === 'lang-switcher-btn' ||
                            (node.closest && node.closest('.notranslate'))) {
                            return NodeFilter.FILTER_REJECT;
                        }

                        // Track placeholders
                        if ((node.tagName === 'INPUT' || node.tagName === 'TEXTAREA') && node.placeholder) {
                            if (!node.dataset.origPlaceholder) {
                                node.dataset.origPlaceholder = node.placeholder;
                            }
                            TRACKED_INPUTS.add(node);
                        }

                        // Track button values
                        if (node.tagName === 'INPUT' && ['button', 'submit', 'reset'].includes(node.type) && node.value) {
                            if (!node.dataset.origValue) {
                                node.dataset.origValue = node.value;
                            }
                            TRACKED_BUTTONS.add(node);
                        }

                        // Track titles
                        if (node.getAttribute && node.getAttribute('title')) {
                            if (!node.dataset.origTitle) {
                                node.dataset.origTitle = node.getAttribute('title');
                            }
                            TRACKED_TITLES.add(node);
                        }

                        return NodeFilter.FILTER_SKIP;
                    } else if (node.nodeType === Node.TEXT_NODE) {
                        // If already recorded, preserve it
                        if (ORIGINAL_TEXTS.has(node)) {
                            TRACKED_TEXT_NODES.add(node);
                            return NodeFilter.FILTER_ACCEPT;
                        }

                        const text = (node.nodeValue || '').trim();
                        // Only capture nodes containing English letters (A-Za-z) and length > 1
                        if (text.length > 1 && /[A-Za-z]/.test(text)) {
                            ORIGINAL_TEXTS.set(node, node.nodeValue);
                            node._ssOrigText = node.nodeValue;
                            TRACKED_TEXT_NODES.add(node);
                            return NodeFilter.FILTER_ACCEPT;
                        }
                        return NodeFilter.FILTER_REJECT;
                    }
                    return NodeFilter.FILTER_SKIP;
                }
            }
        );

        while (walker.nextNode()) {
            // Traversal populates TRACKED_TEXT_NODES
        }
    }

    // ─── 3. GOOGLE TRANSLATOR API BATCH FETCH ────────────────────────────────
    let currentTranslationId = 0;
    let isTranslating = false;

    async function fetchGoogleTranslations(texts, targetLang) {
        if (!texts || texts.length === 0 || targetLang === 'en') return {};

        const results = {};
        const toFetch = [];

        for (const t of texts) {
            const cached = getCache(targetLang, t);
            if (cached) {
                results[t] = cached;
            } else if (CORE_KEYWORDS[t] && CORE_KEYWORDS[t][targetLang]) {
                const tr = CORE_KEYWORDS[t][targetLang];
                setCache(targetLang, t, tr);
                results[t] = tr;
            } else {
                toFetch.push(t);
            }
        }

        if (toFetch.length > 0) {
            try {
                // Batch concurrently in chunks of 35
                const chunkSize = 35;
                const chunkPromises = [];

                for (let i = 0; i < toFetch.length; i += chunkSize) {
                    const chunk = toFetch.slice(i, i + chunkSize);
                    const promise = fetch('/api/translate', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ texts: chunk, target: targetLang })
                    })
                    .then(resp => resp.ok ? resp.json() : { translations: chunk })
                    .then(data => {
                        const translations = data.translations || [];
                        chunk.forEach((orig, idx) => {
                            const tr = translations[idx] || orig;
                            setCache(targetLang, orig, tr);
                            results[orig] = tr;
                        });
                    })
                    .catch(err => {
                        console.warn('Translate API batch error:', err);
                        chunk.forEach(orig => { results[orig] = orig; });
                    });

                    chunkPromises.push(promise);
                }

                await Promise.all(chunkPromises);
            } catch (err) {
                console.warn('Google Translate API request failed:', err);
                toFetch.forEach(orig => { results[orig] = orig; });
            }
        }

        return results;
    }

    // ─── 4. TRANSLATION RUNNER (English <-> Marathi <-> Hindi) ───────────────
    async function translateFullPage(targetLang) {
        if (!targetLang) targetLang = localStorage.getItem('app_language') || 'en';
        localStorage.setItem('app_language', targetLang);
        document.documentElement.lang = targetLang;

        // Keep Google Translate widget cookies purged
        purgeGoogTransCookies();

        // Increment generation token to invalidate any older in-flight translation
        const thisTranslationId = ++currentTranslationId;

        // Ensure all current DOM originals are captured
        captureOriginals(document.body);

        // 1. Navigation items with data-i18n
        const navDict = FAST_NAV[targetLang] || FAST_NAV.en;
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (navDict[key]) {
                el.textContent = navDict[key];
            }
        });

        // 2. Language Switcher Button Label
        const labelEl = document.getElementById('current-lang-label');
        if (labelEl) {
            labelEl.textContent = navDict.current_label || (targetLang === 'mr' ? 'मराठी' : targetLang === 'hi' ? 'हिंदी' : 'English');
        }

        // ─── 4A. INSTANT ENGLISH RESTORATION ───
        if (targetLang === 'en') {
            TRACKED_TEXT_NODES.forEach(node => {
                if (!node || !node.parentNode) return;
                const orig = ORIGINAL_TEXTS.get(node) || node._ssOrigText;
                if (typeof orig !== 'undefined') {
                    node.nodeValue = orig;
                }
            });

            TRACKED_INPUTS.forEach(el => {
                if (el && el.dataset && el.dataset.origPlaceholder) {
                    el.placeholder = el.dataset.origPlaceholder;
                }
            });

            TRACKED_BUTTONS.forEach(el => {
                if (el && el.dataset && el.dataset.origValue) {
                    el.value = el.dataset.origValue;
                }
            });

            TRACKED_TITLES.forEach(el => {
                if (el && el.dataset && el.dataset.origTitle) {
                    el.setAttribute('title', el.dataset.origTitle);
                }
            });

            if (window.lucide && typeof window.lucide.createIcons === 'function') {
                window.lucide.createIcons();
            }
            return;
        }

        // ─── 4B. TRANSLATION TO HINDI OR MARATHI ───
        // Show subtle spinner in language button during first-time fetch
        if (labelEl) {
            labelEl.innerHTML = `<span class="spinner-border spinner-border-sm me-1" style="width: 10px; height: 10px;" role="status"></span> ${navDict.current_label}`;
        }

        // Collect unique original English phrases
        const uniqueTexts = new Set();

        TRACKED_TEXT_NODES.forEach(node => {
            if (!node || !node.parentNode) return;
            const fullOrig = ORIGINAL_TEXTS.get(node) || node._ssOrigText;
            if (fullOrig) {
                const trimmed = fullOrig.trim();
                if (trimmed.length > 1 && /[A-Za-z]/.test(trimmed)) {
                    uniqueTexts.add(trimmed);
                }
            }
        });

        TRACKED_INPUTS.forEach(el => {
            if (el && el.dataset && el.dataset.origPlaceholder) {
                const trimmed = el.dataset.origPlaceholder.trim();
                if (trimmed.length > 1 && /[A-Za-z]/.test(trimmed)) {
                    uniqueTexts.add(trimmed);
                }
            }
        });

        TRACKED_BUTTONS.forEach(el => {
            if (el && el.dataset && el.dataset.origValue) {
                const trimmed = el.dataset.origValue.trim();
                if (trimmed.length > 1 && /[A-Za-z]/.test(trimmed)) {
                    uniqueTexts.add(trimmed);
                }
            }
        });

        TRACKED_TITLES.forEach(el => {
            if (el && el.dataset && el.dataset.origTitle) {
                const trimmed = el.dataset.origTitle.trim();
                if (trimmed.length > 1 && /[A-Za-z]/.test(trimmed)) {
                    uniqueTexts.add(trimmed);
                }
            }
        });

        // Fetch translations concurrently via Google Translator API proxy
        const textArray = Array.from(uniqueTexts);
        const translationsMap = await fetchGoogleTranslations(textArray, targetLang);

        // Check if user changed language while fetch was in flight
        if (thisTranslationId !== currentTranslationId) {
            return; // Discard stale translation response
        }

        // Apply translations to DOM text nodes while strictly preserving whitespace
        TRACKED_TEXT_NODES.forEach(node => {
            if (!node || !node.parentNode) return;
            const fullOrig = ORIGINAL_TEXTS.get(node) || node._ssOrigText;
            if (!fullOrig) return;

            const orig = fullOrig.trim();
            if (translationsMap[orig]) {
                const tr = translationsMap[orig];
                const leadingSpace = (fullOrig.match(/^\s*/) || [''])[0];
                const trailingSpace = (fullOrig.match(/\s*$/) || [''])[0];
                node.nodeValue = leadingSpace + tr + trailingSpace;
            }
        });

        // Apply translations to input placeholders
        TRACKED_INPUTS.forEach(el => {
            if (!el || !el.dataset || !el.dataset.origPlaceholder) return;
            const orig = el.dataset.origPlaceholder.trim();
            if (translationsMap[orig]) {
                el.placeholder = translationsMap[orig];
            }
        });

        // Apply translations to input button values
        TRACKED_BUTTONS.forEach(el => {
            if (!el || !el.dataset || !el.dataset.origValue) return;
            const orig = el.dataset.origValue.trim();
            if (translationsMap[orig]) {
                el.value = translationsMap[orig];
            }
        });

        // Apply translations to title tooltips
        TRACKED_TITLES.forEach(el => {
            if (!el || !el.dataset || !el.dataset.origTitle) return;
            const orig = el.dataset.origTitle.trim();
            if (translationsMap[orig]) {
                el.setAttribute('title', translationsMap[orig]);
            }
        });

        // Restore language switcher button label cleanly
        if (labelEl) {
            labelEl.textContent = navDict.current_label;
        }

        // Re-render Lucide icons
        if (window.lucide && typeof window.lucide.createIcons === 'function') {
            window.lucide.createIcons();
        }
    }

    // ─── 5. PUBLIC LANGUAGE SELECTOR API ─────────────────────────────────────
    window.setAppLanguage = async function (lang) {
        if (isTranslating) return;
        isTranslating = true;
        try {
            await translateFullPage(lang);
            const label = (lang === 'mr' ? 'मराठी' : lang === 'hi' ? 'हिंदी' : 'English');
            const toastMsg = (lang === 'mr' ? 'भाषा बदलली - ' : lang === 'hi' ? 'भाषा बदली गई - ' : 'Language restored to ') + label;
            if (typeof window.showToast === 'function') {
                window.showToast(toastMsg, 'info');
            }
        } finally {
            isTranslating = false;
        }
    };

    window.translateFullPage = translateFullPage;

    // ─── 6. DYNAMIC CONTENT OBSERVER (Modals, Activity Feed, AJAX) ───────────
    let debounceTimer = null;
    const mutationObserver = new MutationObserver(mutations => {
        const currentLang = localStorage.getItem('app_language') || 'en';
        if (isTranslating) return;

        let hasNewNodes = false;
        mutations.forEach(m => {
            if (m.addedNodes && m.addedNodes.length > 0) {
                for (let n of m.addedNodes) {
                    if (n.nodeType === Node.ELEMENT_NODE) {
                        // Ignore mutations inside the language switcher
                        if (n.id === 'lang-switcher-btn' || (n.closest && n.closest('.notranslate'))) {
                            continue;
                        }
                        hasNewNodes = true;
                        break;
                    }
                }
            }
        });

        if (hasNewNodes) {
            if (debounceTimer) clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                if (currentLang !== 'en') {
                    translateFullPage(currentLang);
                } else {
                    captureOriginals(document.body);
                }
            }, 300);
        }
    });

    // ─── 7. INITIALIZATION ON DOM READY ──────────────────────────────────────
    function init() {
        purgeGoogTransCookies();
        // 1. Immediately capture pristine English baseline from server-rendered HTML
        captureOriginals(document.body);

        // 2. Start observing dynamic DOM additions
        mutationObserver.observe(document.body, { childList: true, subtree: true });

        // 3. Restore saved language if user previously chose Hindi or Marathi
        const savedLang = localStorage.getItem('app_language') || 'en';
        if (savedLang !== 'en') {
            setTimeout(() => {
                translateFullPage(savedLang);
            }, 50);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
