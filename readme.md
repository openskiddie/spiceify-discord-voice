# Spicetify Discord VC Tracker

A custom Spicetify extension that injects a live Discord Voice Channel widget directly into the Spotify sidebar. It displays the current channel, active members, and live speaking indicators.

 Installation (Windows)

We've included an automated setup script to make installation as easy as possible. 

1. Download or clone this repository to your computer.
2. Right-click on `setup.ps1` and select **Run with PowerShell**.
   * *Note: This script will automatically check for and safely install Python and Spicetify if you don't already have them. It will also install the required Python packages and copy the extension to Spotify.*

Configuration (Required)

Because Discord's Local RPC requires OAuth authentication, the Python bridge needs an access token to read your voice channel data. **You must add your own token to the Python script before running it.**

### How to get your token:
1. Open your web browser and go to this exact URL (the official Discord authorization page for the StreamKit overlay):
   `https://discord.com/oauth2/authorize?client_id=207646673902501888&redirect_uri=https%3A%2F%2Fstreamkit.discord.com%2Foverlay&response_type=token&scope=rpc`
2. Click the blue **Authorize** button.
3. You will be redirected to a blank StreamKit page. Look at your browser's address bar. 
4. Copy the string of letters and numbers located immediately after `access_token=` and right before `&token_type`.
5. Open `discord_bridge.py` in a text editor.
6. Find the `ACCESS_TOKEN = "YOUR_TOKEN_HERE"` line near the top of the file and paste your token inside the quotes.

Running the Tracker

The Spicetify extension relies on the Python bridge to securely talk to Discord. 

**To run it manually:**
1. Open a terminal in the folder containing these files.
2. Run the Python bridge: `python discord_bridge.py`
3. Join a voice channel in Discord. Your Spotify sidebar will instantly update!

---

Automating the Bridge (Run on Startup)

If you don't want to manually start the Python script every time you restart your PC, you can configure it to run silently in the background on startup.

1. Open Notepad and paste the following code:
   ```vbscript
   Set WshShell = CreateObject("WScript.Shell")
   WshShell.Run "pythonw.exe """ & CreateObject("Scripting.FileSystemObject").GetAbsolutePathName(".") & "\discord_bridge.py""", 0
   Set WshShell = Nothing
Save this file in your project folder as start_bridge.vbs. (Ensure "Save as type" is set to "All Files" so it doesn't save as a .txt).

Press Win + R, type shell:startup, and press Enter. This opens your Windows Startup folder.

Right-click your new start_bridge.vbs file, select Create shortcut, and drag that shortcut into the Startup folder.