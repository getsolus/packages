// Ask the user what he wants to do when an update is available (True will download and install automatically)
pref("app.update.auto",                     false);
// Disable auto install update
pref("app.update.autoInstallEnabled",       false);
// Disable auto update
pref("app.update.enabled",                  false);
// Pressing [Backspace] will go back a page in the session history and [Shift]+[Backspace] will go forward
pref("browser.backspace_action",            0);
// Open links from external programs in new tabs in an existing window
pref("browser.link.open_external",          3);
pref("browser.newtabpage.activity-stream.disableSnippets", true);
pref("browser.newtabpage.activity-stream.feeds.snippets", false);
pref("browser.newtabpage.pinned",           '[{"url":"https://getsol.us/blog/","title":"Blogs | Solus"}]');
// Default browser check
pref("browser.shell.checkDefaultBrowser",   false);
// Set default homepage
pref("browser.startup.homepage",            "data:text/plain,browser.startup.homepage=https://getsol.us/blog/");
// Needed for loading langpacks
pref("extensions.autoDisableScopes",        0);
// Do not recommend extensions
pref("extensions.htmlaboutaddons.recommendations.enabled", false);
// Display settings for the extension being installed
pref("extensions.shownSelectionUI",         true);
// Content Security Policy for WebExtensions
pref("extensions.webextensions.base-content-security-policy", "script-src 'self' https://* moz-extension: blob: filesystem: 'unsafe-eval' 'unsafe-inline'; object-src 'self' https://* moz-extension: blob: filesystem:;");
// Enable smooth scrolling
pref("general.smoothScroll",                true);
// Geolocation preferences
pref("geo.provider.network.url", "https://api.beacondb.net/v1/geolocate");
pref("geo.wifi.uri", "https://api.beacondb.net/v1/geolocate");
pref("layers.use-image-offscreen-surfaces", false);
// Enable MSE (Media Source Extensions) API
pref("media.mediasource.enabled",           true);
// Enable MSE Webm media streams
pref("media.mediasource.webm.enabled",      true);
// Whether IOService.connectivity and NS_IsOffline depends on connectivity status
pref("network.manage-offline-status",       true);
pref("offline.autoDetect",                  true);
pref("spellchecker.dictionary_path", "/usr/share/hunspell");
// Default homepage override URL
pref("startup.homepage_override_url",       "");
// False = Use NetworkManager to detect offline/online status, and switch between offline/online modes in Firefox
pref("toolkit.networkmanager.disable",      false);
pref("toolkit.storage.synchronous",         0);
pref("ui.context_menus.after_mouseup",      true);
// Override theme to prevent local dark themes affecting how website content is displayed
pref("widget.content.gtk-theme-override","Adwaita:light");
// Use XDG Desktop Portals for filepicker by default
pref("widget.use-xdg-desktop-portal.file-picker", 1);
// Allow gnome search provider to function by default
pref("browser.gnome-search-provider.enabled", true);
