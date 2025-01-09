(async () => {
    /**
     * Wait for a specific element to appear within a timeout
     * @param {string} selector - CSS selector for the target element
     * @param {number} timeout - Maximum time to wait in milliseconds
     * @returns {Promise<Element>} Resolves with the element or rejects on timeout
     */
    const waitForElement = (selector, timeout = 5000) => {
        return new Promise((resolve, reject) => {
            const interval = 100;
            const endTime = Date.now() + timeout;

            const check = () => {
                const element = document.querySelector(selector);
                if (element) resolve(element);
                else if (Date.now() > endTime) reject(`Timeout waiting for selector: ${selector}`);
                else setTimeout(check, interval);
            };

            check();
        });
    };

    /**
     * Wait for an element's innerText to be non-empty
     * @param {string} selector - CSS selector for the target element
     * @param {number} timeout - Maximum time to wait in milliseconds
     * @returns {Promise<Element>} Resolves with the element or rejects on timeout
     */
    const waitForNonEmptyText = (selector, timeout = 5000) => {
        return new Promise((resolve, reject) => {
            const interval = 100;
            const endTime = Date.now() + timeout;

            const check = () => {
                const element = document.querySelector(selector);
                if (element && element.innerText.trim() !== "") resolve(element);
                else if (Date.now() > endTime) reject(`Timeout waiting for non-empty text in selector: ${selector}`);
                else setTimeout(check, interval);
            };

            check();
        });
    };

    /**
     * Extract text content from the #detail-desc div
     * @returns {string|null} Cleaned text content or null if the element is missing
     */
    const extractText = async () => {
        const detailDesc = await waitForNonEmptyText("#detail-desc");
        if (!detailDesc) return null;

        // Remove unnecessary whitespace and clean text
        return detailDesc.innerText.replace(/\s+/g, " ").trim();
    };

    /**
     * Main function to extract text from all posts
     */
    const extractAllPosts = async () => {
        const posts = Array.from(document.querySelectorAll("section.note-item")); // Get all post items
        const extractedTexts = []; // Store extracted texts

        for (let i = 0; i < posts.length; i++) {
            const post = posts[i];
            const clickableLink = post.querySelector("a.cover.ld.mask");

            if (!clickableLink) {
                console.warn(`Post ${i + 1} does not have a clickable link. Skipping.`);
                continue;
            }

            console.log(`Processing post ${i + 1} of ${posts.length}`);

            // Click on the link to open the popup
            clickableLink.click();

            try {
                // Wait for the popup to appear and contain text
                await waitForNonEmptyText("#detail-desc");

                // Extract text from the popup
                const text = await extractText();
                if (text) extractedTexts.push(text);

                // Close the popup
                const closeButton = document.querySelector('div.close.close-mask-dark');
                if (closeButton) closeButton.click();

                // Wait for the popup to close
                await new Promise(resolve => setTimeout(resolve, 500)); // Adjust delay if needed
            } catch (error) {
                console.error(`Error processing post ${i + 1}:`, error);
            }
        }

        console.log("Extraction complete!");
        console.log("Extracted Texts:", extractedTexts);

        // Copy results to clipboard
        const result = JSON.stringify(extractedTexts, null, 2);
        console.log(result);
    };

    // Start the extraction process
    await extractAllPosts();
})();
