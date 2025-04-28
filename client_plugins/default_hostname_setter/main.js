/**
 * Copyright (c) 2025 The Foundry Visionmongers Ltd.  All Rights Reserved.
 * This plugin will only work on Flix Client <= 8.0.0.Beta
 */
function setDefaultHostname() {
    if (!window.location.pathname.includes('login')) {
        return;
    }

    const hostInput = document.querySelector('input[name="host"]');
    if (!hostInput) {
        console.warn('Default Hostname Setter: No input[name="host"] found.');
        return;
    }

    if (hostInput.value.trim() === '') {
        hostInput.value = 'your-default-hostname.com';
        console.info('Default Hostname Setter: Hostname set.');
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setDefaultHostname);
} else {
    setDefaultHostname();
}

