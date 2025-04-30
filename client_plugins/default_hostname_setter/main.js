// Set your default hostname here
const DEFAULT_HOST_NAME = 'your-default-hostname.com'

/**
 * Copyright (c) 2025 The Foundry Visionmongers Ltd.  All Rights Reserved.
 *
 * Sets the default hostname in the hostname input when on the login page and the input value is empty.
 */
function setDefaultHostname() {
    if (!window.location.href.includes('login')) {
        return;
    }

    const hostInput = document.querySelector('input#login_hostname');
    if (!hostInput) {
        console.warn('Default Hostname Setter: No hostname input found found.');
        return;
    }

    if (hostInput.value.trim() === '') {
        hostInput.value = DEFAULT_HOST_NAME;
        console.info('Default Hostname Setter: Hostname set.');
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setDefaultHostname);
} else {
    setDefaultHostname();
}

