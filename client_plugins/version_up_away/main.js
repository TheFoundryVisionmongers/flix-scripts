/**
 * Handles mutation observer events. Filters events down to DOM modification that impact the version up button, and hides it if it is visible.
 */
const onDomChange = (mutations) => {
    for (const mutation of mutations) {
        //  If not an element added/remove, skip this event.
        if (mutation.type !== 'childList') {
            continue;
        }

        const targetElement = mutation.target;
        //  If not the version up button, skip this event.
        if (targetElement.id !== "versionUp") {
            continue;
        }

        //  If the version up button is already hidden, stop processing events.
        if (targetElement.style.display === 'none') {
            break;
        }

        //  Otherwise, hide the version up button and stop processing events.
        console.log("Hiding Version Up button in the Panel Browser.");
        targetElement.style.display = 'none';
        break;
    }
};

//  Mutation observer is used to monitor changes to DOM elements to hide the version up button when it is added.
const observer = new MutationObserver(onDomChange);

//  Flag to determine whether DOM changes are currently being observed.
let observing = false;

//  Navigation API is used to monitor navigating to the panel browser to start watching DOM modifications.
navigation.addEventListener("navigate", event => {
    if (event.destination.url.endsWith("/workspace")) {
        //  When in the panel browser, start watching DOM changes to hide the version up button
        console.log("Detected Flix workspace, listening for DOM changes.");

        observer.observe(document.body, { subtree: true, childList: true });
        observing = true;

        //  If the version up button is already present in the DOM, hide it now
        const versionUpElement = document.querySelector("#versionUp");
        if (versionUpElement) {
            console.log("Hiding Version Up button in the Panel Browser.");
            versionUpElement.style.display = 'none';
        }
    } else if (observing) {
        //  When leaving the panel browser, stop monitoring DOM changes so it doesn't impact performance
        console.log("Left Flix workspace, stopped listening to DOM changes.");

        observer.disconnect();
        observing = false;
    }
});