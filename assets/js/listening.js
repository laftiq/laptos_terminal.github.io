// Public Last.fm read API. No account secret or session token is used.
(() => {
  const config = { user: "lftq", key: "b6780b1559b26694bb16eeabe7ba7772" };
  const root = document.getElementById("listening");
  const title = root.querySelector(".listening-title");
  const artist = root.querySelector(".listening-artist");
  const status = root.querySelector(".listening-status");
  const cover = root.querySelector(".listening-cover");
  const link = document.createElement("a");
  link.href = "https://www.last.fm/user/" + encodeURIComponent(config.user);
  link.target = "_blank";
  link.rel = "noopener noreferrer";
  link.className = "listening-link";
  title.replaceWith(link);
  link.append(title);
  let running = false,
    hasTrack = false,
    lastPlayedAt = null,
    isNowPlaying = false,
    updateFailed = false;
  function renderListeningTime() {
    if (!hasTrack || updateFailed) return;
    if (isNowPlaying) {
      status.textContent = "Listening now";
      return;
    }
    if (!lastPlayedAt) {
      status.textContent = "Last listened";
      return;
    }
    const seconds = Math.max(0, Math.floor(Date.now() / 1000 - lastPlayedAt));
    let relative;
    if (seconds < 60) relative = "just now";
    else if (seconds < 3600) {
      const n = Math.floor(seconds / 60);
      relative = n + " min ago";
    } else if (seconds < 86400) {
      const n = Math.floor(seconds / 3600);
      relative = n + " " + (n === 1 ? "hour" : "hours") + " ago";
    } else {
      const n = Math.floor(seconds / 86400);
      relative = n + " " + (n === 1 ? "day" : "days") + " ago";
    }
    status.textContent = "Last listened · " + relative;
    status.title = new Date(lastPlayedAt * 1000).toLocaleString();
  }
  setInterval(renderListeningTime, 15000);
  async function update() {
    if (running) return;
    running = true;
    try {
      const url = new URL("https://ws.audioscrobbler.com/2.0/");
      url.search = new URLSearchParams({
        method: "user.getRecentTracks",
        user: config.user,
        api_key: config.key,
        format: "json",
        limit: "1",
      });
      const response = await fetch(url, { signal: AbortSignal.timeout(12000) });
      if (!response.ok) throw new Error("HTTP " + response.status);
      const data = await response.json();
      if (data.error) throw new Error("Last.fm " + data.error);
      const tracks = data.recenttracks?.track;
      const track = Array.isArray(tracks) ? tracks[0] : tracks;
      if (!track) {
        title.textContent = "Quiet for now";
        artist.textContent = "No tracks yet";
        status.textContent = "Nothing played yet";
        cover.replaceChildren();
        cover.textContent = "♪";
        hasTrack = false;
        return;
      }
      title.textContent = track.name;
      artist.textContent = track.artist?.["#text"] || track.artist?.name || "";
      const trackUrl = new URL(track.url || link.href);
      if (trackUrl.protocol === "https:") link.href = trackUrl.href;
      const now = track["@attr"]?.nowplaying === "true";
      isNowPlaying = now;
      lastPlayedAt = Number(track.date?.uts) || null;
      updateFailed = false;
      status.removeAttribute("title");
      const image = [...(track.image || [])]
        .reverse()
        .find((i) => i["#text"] && i["#text"].startsWith("https://"));
      cover.replaceChildren();
      if (image) {
        const img = document.createElement("img");
        img.src = image["#text"];
        img.alt = "";
        img.width = 58;
        img.height = 58;
        img.onerror = () => {
          cover.replaceChildren();
          cover.textContent = "♪";
        };
        cover.append(img);
      } else cover.textContent = "♪";
      hasTrack = true;
      renderListeningTime();
    } catch (error) {
      updateFailed = true;
      if (!hasTrack) {
        title.textContent = "Quiet for now";
        artist.textContent = "Music status is unavailable";
      }
      status.textContent = hasTrack ? "Update unavailable" : "Try again shortly";
    } finally {
      running = false;
    }
  }
  update();
  setInterval(() => {
    if (!document.hidden) update();
  }, 45000);
  document.addEventListener("visibilitychange", () => {
    if (!document.hidden) update();
  });
})();
