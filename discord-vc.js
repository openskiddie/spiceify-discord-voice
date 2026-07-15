(function DiscordIntegration() {
    if (!Spicetify.Platform) {
        setTimeout(DiscordIntegration, 1000);
        return;
    }

    console.log("Discord VC Extension Loaded - Attempting Connection...");

    // 1. Build the UI Container (Now with an outline and overflow protection)
    const discordContainer = document.createElement('div');
    discordContainer.id = 'discord-vc-container';
    discordContainer.style.padding = '12px';
    discordContainer.style.margin = '10px 8px';
    discordContainer.style.background = 'var(--spice-card, #282828)';
    discordContainer.style.border = '1px solid var(--spice-button-disabled, rgba(255,255,255,0.15))'; // The outline
    discordContainer.style.borderRadius = '8px';
    discordContainer.style.overflow = 'hidden'; // Prevents anything from spilling out
    
    // Header setup
    discordContainer.innerHTML = `
        <h3 id="vc-header" style="font-size: 13px; margin: 0 0 10px 0; color: var(--spice-text); text-align: center; border-bottom: 1px solid var(--spice-button-disabled, rgba(255,255,255,0.1)); padding-bottom: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
            Voice Channel
        </h3>
        <ul id="vc-list" style="padding: 0; margin: 0; color: var(--spice-subtext);">
            <div style="font-size: 12px; text-align: center;">Connecting to bridge...</div>
        </ul>`;

    // 2. Inject into Spotify's UI using fallback targets
    const injectUI = setInterval(() => {
        const selectors = [
            '.main-yourLibraryX-navBar', 
            '.Root__nav-bar', 
            '.Root__right-sidebar',
            '.main-navBar-navBar',
            '.os-content' 
        ];

        let targetContainer = null;
        
        for (let selector of selectors) {
            targetContainer = document.querySelector(selector);
            if (targetContainer) break;
        }

        if (targetContainer) {
            targetContainer.prepend(discordContainer);
            clearInterval(injectUI);
            console.log("Discord UI Injected.");
        }
    }, 1000);

    // 3. Connect to the Python Bridge IMMEDIATELY
    function startDataConnection() {
        const ws = new WebSocket('ws://127.0.0.1:8765');
        
        ws.onopen = () => {
            console.log("Connected to Python Discord bridge");
            const list = document.getElementById('vc-list');
            const header = document.getElementById('vc-header');
            if(header) header.innerText = "Connected to Bridge";
            if(list) list.innerHTML = `<div style="font-size: 12px; text-align: center;">Waiting for VC...</div>`;
        };
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            updateVCList(data);
        };
        
        ws.onclose = () => {
            console.log("Lost connection to bridge. Retrying in 5s...");
            const list = document.getElementById('vc-list');
            const header = document.getElementById('vc-header');
            if(header) header.innerText = "Disconnected";
            if(list) list.innerHTML = `<div style="font-size: 12px; text-align: center;">Bridge disconnected.</div>`;
            setTimeout(startDataConnection, 5000);
        };
    }

    // 4. Update the UI with live data matching the sketch
    function updateVCList(data) {
        const list = document.getElementById('vc-list');
        const header = document.getElementById('vc-header');
        if (!list || !header) return;
        
        // Set the top title to the channel name
        header.innerText = data.channel_name;
        
        let html = '';
        
        data.members.forEach(member => {
            const isSpeaking = member.speaking;
            const primaryColor = isSpeaking ? '#1DB954' : 'var(--spice-subtext)';
            const textColor = isSpeaking ? 'var(--spice-text)' : 'var(--spice-subtext)';
            
            // Circle indicator: Filled green if speaking, empty grey outline if not
            const circleStyle = `
                width: 10px;
                height: 10px;
                border-radius: 50%;
                border: 2px solid ${primaryColor};
                background-color: ${isSpeaking ? '#1DB954' : 'transparent'};
                flex-shrink: 0;
            `;
            
            const icon = isSpeaking ? '🔊' : ''; // Only show icon when speaking
            
            // Flexbox layout to keep everything inline and stop text run-down
            html += `
                <li style="color: ${textColor}; list-style: none; font-size: 13px; margin-bottom: 8px; display: flex; align-items: center; gap: 10px; overflow: hidden;">
                    <div style="${circleStyle}"></div>
                    <span style="flex-grow: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${member.name}">${member.name}</span>
                    <span style="flex-shrink: 0; font-size: 14px; width: 16px; text-align: right;">${icon}</span>
                </li>`;
        });

        // Handle empty states
        if (data.members.length === 0 && data.channel_name !== "Not in VC") {
             html = `<div style="font-size: 12px; text-align: center;">Empty Channel</div>`;
        } else if (data.channel_name === "Not in VC") {
             html = `<div style="font-size: 12px; text-align: center;">Waiting for VC...</div>`;
        }
        
        list.innerHTML = html;
    }

    // Start the connection logic right away
    startDataConnection();
})();