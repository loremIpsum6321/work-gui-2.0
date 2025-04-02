    // --- DOM Elements ---
    const searchInput = document.getElementById('searchInput');
    const suggestionsList = document.getElementById('suggestionsList');
    const itemDetailsContainer = document.getElementById('itemDetails');
    const detailGrd = document.getElementById('detailGrd');
    const detailDescription = document.getElementById('detailDescription');
    const detailPriceKg = document.getElementById('detailPriceKg');
    const detailPriceLb = document.getElementById('detailPriceLb');
    const detailCategory = document.getElementById('detailCategory');
    const detailNotes = document.getElementById('detailNotes');
    const copyNotification = document.getElementById('copyNotification');
    const timeElement = document.getElementById('current-time'); // For footer time
    // --- Event Listener: Click Input to Clear ---
    searchInput.addEventListener('click', () => {
        // Only clear if it already has some value
        if (searchInput.value !== '') {
            searchInput.value = ''; // Clear the input field
            clearSuggestions();     // Clear the suggestions dropdown
            displayItemDetails(null); // Clear the details panel
            highlightedIndex = -1;  // Reset highlight index
        }
        // Note: We don't explicitly call searchInput.focus() here,
        // as the click event itself implies the input is gaining focus.
    });
    // --- State Variables ---
    let allItems = []; // To store data from items.json
    let filteredItems = []; // To store currently filtered suggestions
    let highlightedIndex = -1; // Index of the currently highlighted suggestion (-1 = none)
    const MAX_SUGGESTIONS = 8; // Max suggestions to show

    // --- Fetch Item Data ---
    async function loadItems() {
        try {
            const response = await fetch('items.json');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            allItems = await response.json();
            // console.log('Items loaded:', allItems); // For debugging
        } catch (error) {
            console.error("Could not load items:", error);
            suggestionsList.innerHTML = '<li class="suggestion-item">Error loading items.</li>';
        }
    }

    // --- Display Suggestions ---
    function displaySuggestions(items) {
        suggestionsList.innerHTML = ''; // Clear previous suggestions
        if (items.length === 0 && searchInput.value.trim() !== '') {
            suggestionsList.innerHTML = '<li class="suggestion-item">No matching items found.</li>';
            return;
        }

        items.slice(0, MAX_SUGGESTIONS).forEach((item, index) => {
            const li = document.createElement('li');
            li.classList.add('suggestion-item');
            li.textContent = `${item.grd} - ${item.description}`;
            li.dataset.index = index; // Store index for easy lookup

            // Mouse hover listener
            li.addEventListener('mouseover', () => {
                highlightedIndex = index;
                highlightSuggestion(highlightedIndex); // Highlight visually
                displayItemDetails(item); // Display details
            });

            // Mouse click listener (optional, good for touch/quick select)
            li.addEventListener('click', () => {
                searchInput.value = `${item.grd} - ${item.description}`; // Fill input
                displayItemDetails(item); // Show details
                copyToClipboard(item.grd, "GRD"); // Copy GRD on click too
                clearSuggestions();
            });

            suggestionsList.appendChild(li);
        });
    }

    // --- Clear Suggestions ---
    function clearSuggestions() {
        suggestionsList.innerHTML = '';
        filteredItems = [];
        highlightedIndex = -1;
    }

    // --- Display Item Details ---
    function displayItemDetails(item) {
        if (!item) { // Clear details if no item
            detailGrd.textContent = '-';
            detailDescription.textContent = '-';
            detailPriceKg.textContent = '-';
            detailPriceLb.textContent = '-';
            detailCategory.textContent = '-';
            detailNotes.textContent = '-';
            return;
        }
        detailGrd.textContent = item.grd || '-';
        detailDescription.textContent = item.description || '-';
        detailPriceKg.textContent = item.price_kg ? `$${item.price_kg.toFixed(2)}` : '-';
        detailPriceLb.textContent = item.price_lb ? `$${item.price_lb.toFixed(2)}` : '-';
        detailCategory.textContent = item.category || '-';
        detailNotes.textContent = item.notes || '-';
        // Update other detail spans if you added more
    }

    // --- Highlight Suggestion (Visual) ---
    function highlightSuggestion(index) {
        const suggestions = suggestionsList.querySelectorAll('.suggestion-item');
        suggestions.forEach((li, i) => {
            if (i === index) {
                li.classList.add('highlighted');
                // Ensure the highlighted item is visible in the scrollable list
                li.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
            } else {
                li.classList.remove('highlighted');
            }
        });
    }

    // --- Copy to Clipboard ---
    async function copyToClipboard(text, type) {
        if (!text || text.trim() === "") {
            console.error("Cannot copy empty or null text.");
            showCopyNotification(`Failed to copy ${type}!`);
            return;
        }

        const trimmedText = text.trim();

        try {
            if (navigator.clipboard && navigator.clipboard.writeText) {
                // Use modern Clipboard API if available
                await navigator.clipboard.writeText(trimmedText);
            } else {
                // Fallback to execCommand for environments without Clipboard API
                const textarea = document.createElement("textarea");
                textarea.value = trimmedText;
                textarea.style.position = "fixed"; // Prevent scrolling to the bottom
                document.body.appendChild(textarea);
                textarea.focus();
                textarea.select();
                const successful = document.execCommand("copy");
                document.body.removeChild(textarea);

                if (!successful) {
                    throw new Error("Fallback copy failed.");
                }
            }
            showCopyNotification(`${type} copied to clipboard!`);
        } catch (err) {
            console.error("Failed to copy text: ", err);
            showCopyNotification(`Failed to copy ${type}!`);
        }
    }

    // --- Event Listener: Search Input ---
    searchInput.addEventListener('input', () => {
        const searchTerm = searchInput.value.toLowerCase().trim();
        if (searchTerm === '') {
            clearSuggestions();
            displayItemDetails(null); // Clear details when input is empty
            return;
        }

        filteredItems = allItems.filter(item =>
            item.grd.toLowerCase().startsWith(searchTerm) ||
            item.description.toLowerCase().includes(searchTerm)
        );

        highlightedIndex = -1; // Reset highlight when typing
        if (filteredItems.length > 0) {
            highlightedIndex = 0; // Auto-select the first item
            highlightSuggestion(highlightedIndex);
        }
        displaySuggestions(filteredItems);
    });

    // --- Event Listener: Keyboard Navigation ---
    searchInput.addEventListener('keydown', (event) => {
        const { key } = event;
        const suggestionsCount = suggestionsList.querySelectorAll('.suggestion-item').length;

        if (suggestionsCount === 0 && !['Escape'].includes(key)) return; // Only allow Escape if no suggestions

        let preventDefault = false; // Flag to prevent default actions

        switch (key) {
            case 'ArrowDown':
                preventDefault = true;
                highlightedIndex++;
                if (highlightedIndex >= suggestionsCount) {
                    highlightedIndex = 0; // Wrap around
                }
                highlightSuggestion(highlightedIndex);
                if (highlightedIndex >= 0 && highlightedIndex < filteredItems.length) {
                    displayItemDetails(filteredItems[highlightedIndex]); // Show details on arrow key
                }
                break;

            case 'ArrowUp':
                preventDefault = true;
                highlightedIndex--;
                if (highlightedIndex < 0) {
                    highlightedIndex = suggestionsCount - 1; // Wrap around
                }
                highlightSuggestion(highlightedIndex);
                if (highlightedIndex >= 0 && highlightedIndex < filteredItems.length) {
                    displayItemDetails(filteredItems[highlightedIndex]); // Show details on arrow key
                }
                break;

            case 'Enter':
                preventDefault = true; // Prevent form submission
                if (highlightedIndex !== -1) {
                    const selectedItem = filteredItems[highlightedIndex];
                    if (selectedItem) {
                        copyToClipboard(selectedItem.grd, "GRD");
                        searchInput.value = `${selectedItem.grd} - ${selectedItem.description}`; // Optional: Fill input
                        clearSuggestions(); // Clear suggestions after selection
                        // Optionally, keep details displayed or clear them too
                    }
                }
                break;

            case 'Escape':
                preventDefault = true; // Prevent closing modals etc.
                clearSuggestions();
                searchInput.value = ''; // Clear input field on Escape
                displayItemDetails(null); // Clear details
                break;
        }

        if (preventDefault) {
            event.preventDefault();
        }
    });

    function showCopyNotification(message) {
        const copyNotification = document.getElementById("copyNotification");
        if (copyNotification) {
            copyNotification.textContent = message;
            copyNotification.classList.add("show");
            setTimeout(() => {
                copyNotification.classList.remove("show");
            }, 2000);
        }
    }
    // --- Event Listener: Click Outside Suggestions ---
    document.addEventListener('click', (event) => {
        // If the click is not on the search input or the suggestions list
        if (!searchInput.contains(event.target) && !suggestionsList.contains(event.target)) {
            clearSuggestions(); // Hide suggestions when clicking away
        }
    });

    // ==========================================
    document.addEventListener('DOMContentLoaded', () => {
    // == SMOOTH MOUSE-FOLLOWING GLOW EFFECT ==
    // ==========================================    
        const bodyElementForGlow = document.body; // Re-declare if needed, or reuse existing body var
        const glowConfig = {
            glowSize: 900,                  // Size of the glow circle in pixels
            baseColorRGB: "168, 85, 247",   // RGB values for the glow purple color (without 'rgba()')
            baseAlpha: 0.06,                // Base intensity/opacity (0.0 - 1.0)
            fadeStop: 0.6                   // Where the glow fades to transparent (0.0 - 1.0, e.g., 0.7 = 70%)
        };
        // Apply a static glow
        const staticGradient = `radial-gradient(circle ${glowConfig.glowSize * 0.5}px at 50% 20%, rgba(${glowConfig.baseColorRGB}, ${glowConfig.baseAlpha * 0.5}) 0%, rgba(${glowConfig.baseColorRGB}, 0) ${glowConfig.fadeStop * 100}%)`;
        bodyElementForGlow.style.backgroundImage = staticGradient;

    });

    // --- Footer Time ---
    function displayTime() {
        if (!timeElement) return; // Only run if element exists
        const options = { timeZone: 'America/Los_Angeles', hour: 'numeric', minute: 'numeric', second: 'numeric', hour12: true };
        const formatter = new Intl.DateTimeFormat([], options);
        const currentTime = formatter.format(new Date());
        timeElement.textContent = currentTime;
    }
    setInterval(displayTime, 1000);
    displayTime(); // Initial call

    // --- Copy to Clipboard Functionality for Detail Lines ---
    const copyButtons = document.querySelectorAll('.copy-button');
    copyButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetId = button.dataset.copyTarget;
            const targetSpan = document.getElementById(targetId);

            if (targetSpan) {
                const textToCopy = targetSpan.textContent;
                const type = targetId.replace('detail', '');
                copyToClipboard(textToCopy, type);
            }
        });
    });

    // --- Initial Load ---
    loadItems(); // Load data when the page is ready
    displayItemDetails(null); // Start with empty details
