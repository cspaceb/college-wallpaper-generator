/* ----------------------------------------------------
   DEVICE DEFAULT WALLPAPER TYPE
---------------------------------------------------- */

function updateDefaultWallpaperType() {
    const typeSelect = document.getElementById("typeSelect");
    typeSelect.value = window.innerWidth <= 800 ? "mobile" : "pc";
}

window.addEventListener("load", updateDefaultWallpaperType);
window.addEventListener("resize", updateDefaultWallpaperType);


/* ----------------------------------------------------
   MAIN ELEMENTS
---------------------------------------------------- */

let selectedTeam = null;
let stickerBombEnabled = false;

const dropdownSelected = document.getElementById("teamSelected");
const dropdownList = document.getElementById("teamList");

const colorPicker = document.getElementById("colorPicker");
const colorHex = document.getElementById("colorHex");

const gradColor2 = document.getElementById("gradColor2");
const gradHex2 = document.getElementById("gradHex2");

const gradientToggle = document.getElementById("gradientToggle");
const gradientOptions = document.getElementById("gradientOptions");
const gradientStyle = document.getElementById("gradientStyle");

const angleSlider = document.getElementById("angleSlider");
const angleValue = document.getElementById("angleValue");
const angleWrapper = document.getElementById("angleWrapper");

const noiseDetailWrapper = document.getElementById("noiseDetailWrapper");
const noiseDetail = document.getElementById("noiseDetail");

const colorPreview = document.getElementById("colorPreview");
const previewTeamLogo = document.getElementById("previewTeamLogo");

const typeSelect = document.getElementById("typeSelect");
const stickerBombToggle = document.getElementById("stickerBombToggle");

const generateBtn = document.getElementById("generateBtn");


/* ----------------------------------------------------
   LOADING OVERLAY
---------------------------------------------------- */

const loadingOverlay = document.createElement("div");
loadingOverlay.id = "loadingOverlay";
loadingOverlay.innerHTML = `
    <div class="loading-spinner"></div>
    <div class="loading-text">Generating Wallpaper...</div>
`;
document.body.appendChild(loadingOverlay);

function showLoading() {
    loadingOverlay.style.display = "flex";
    generateBtn.disabled = true;
}

function hideLoading() {
    loadingOverlay.style.display = "none";
    generateBtn.disabled = false;
}


/* ----------------------------------------------------
   TEAM COLORS
---------------------------------------------------- */

async function fetchTeamColors(teamName) {
    const res = await fetch(`/team-colors?team=${encodeURIComponent(teamName)}`);
    if (!res.ok) return null;
    return await res.json();
}

async function applyTeamColors(teamName) {
    const colors = await fetchTeamColors(teamName);
    if (!colors) return;

    colorPicker.value = colors.primary;
    colorHex.value = colors.primary;

    gradColor2.value = colors.secondary;
    gradHex2.value = colors.secondary;

    refreshPreview();
}


/* ----------------------------------------------------
   PREVIEW ENGINE — Fixed Angles + Split Mode + Stroke
---------------------------------------------------- */

function setPreviewGradient(css) {
    colorPreview.style.background = css;
}

function refreshPreview() {
    const type = typeSelect.value;

    /* ============================
       STICKERBOMB PREVIEW
    ============================ */
    if (stickerBombEnabled) {
        const previewImage =
            type === "pc"
                ? "/data/stickerbomb/pc.png"
                : "/data/stickerbomb/mobile.png";

        colorPreview.style.background = `url('${previewImage}') center/cover no-repeat`;

        if (selectedTeam) {
            previewTeamLogo.style.display = "block";
            previewTeamLogo.src = `/data/logos/${selectedTeam.replace(/ /g, "_")}.png`;
        } else {
            previewTeamLogo.style.display = "none";
        }

        return;
    }

    /* ============================
       NORMAL MODE PREVIEW
    ============================ */

    if (selectedTeam) {
        previewTeamLogo.style.display = "block";
        previewTeamLogo.src = `/data/logos/${selectedTeam.replace(/ /g, "_")}.png`;
    } else {
        previewTeamLogo.style.display = "none";
    }

    if (!gradientToggle.checked) {
        colorPreview.style.background = colorPicker.value;
        return;
    }

    // FIX: CSS angle reversed vs Pillow
    const correctedAngle = (360 - angleSlider.value) % 360;

    const c1 = colorPicker.value;
    const c2 = gradColor2.value;
    let gradientCSS = "";

    switch (gradientStyle.value) {

        case "linear":
            gradientCSS = `linear-gradient(${correctedAngle}deg, ${c1}, ${c2})`;
            break;

        case "radial":
            gradientCSS = `radial-gradient(circle, ${c1}, ${c2})`;
            break;

        case "diamond":
            gradientCSS = `radial-gradient(circle at top left, ${c1}, ${c2})`;
            break;

        case "fade": {
            const darker = shadeColor(c1, -40);
            gradientCSS = `linear-gradient(180deg, ${c1}, ${darker})`;
            break;
        }

        case "split": {
            // Python produces top/bottom based on midpoint of rotated diag gradient.
            // CSS reverses this for 0° and 180°.
            const reversed = (correctedAngle === 0 || correctedAngle === 180);
            const startColor = reversed ? c2 : c1;
            const endColor = reversed ? c1 : c2;

            gradientCSS = `linear-gradient(${correctedAngle}deg, ${startColor} 50%, ${endColor} 50%)`;
            break;
        }

        case "mirror":
            gradientCSS = `linear-gradient(${correctedAngle}deg, ${c1}, ${c2}, ${c1})`;
            break;

        case "noise":
            gradientCSS = `
                linear-gradient(180deg, ${c1}, ${c2}),
                repeating-linear-gradient(
                    45deg,
                    rgba(255,255,255,0.06) 0px,
                    rgba(255,255,255,0.06) 2px,
                    rgba(0,0,0,0.06) 2px,
                    rgba(0,0,0,0.06) 4px
                )
            `;
            break;
    }

    setPreviewGradient(gradientCSS);
}


/* ----------------------------------------------------
   UI DISABLES FOR STICKERBOMB MODE
---------------------------------------------------- */

function applyStickerBombState() {
    stickerBombEnabled = stickerBombToggle.checked;

    const disable = stickerBombEnabled;

    const colorSection = document.getElementById("colorSection");
    const gradientSection = document.getElementById("gradientToggleSection");

    colorSection.style.opacity = disable ? "0.3" : "1";
    colorSection.style.pointerEvents = disable ? "none" : "auto";

    gradientSection.style.opacity = disable ? "0.3" : "1";
    gradientSection.style.pointerEvents = disable ? "none" : "auto";

    gradientOptions.classList.toggle("hidden", disable || !gradientToggle.checked);

    refreshPreview();
}

stickerBombToggle.addEventListener("change", applyStickerBombState);


/* ----------------------------------------------------
   GRADIENT OPTION VISIBILITY
---------------------------------------------------- */

function updateAngleVisibility() {
    angleWrapper.classList.toggle(
        "hidden",
        !gradientToggle.checked ||
            !["linear", "mirror", "split"].includes(gradientStyle.value)
    );
}

function updateNoiseVisibility() {
    noiseDetailWrapper.classList.toggle(
        "hidden",
        !(gradientToggle.checked && gradientStyle.value === "noise")
    );
}

gradientStyle.addEventListener("change", () => {
    updateAngleVisibility();
    updateNoiseVisibility();
    refreshPreview();
});

gradientToggle.addEventListener("change", () => {
    gradientOptions.classList.toggle("hidden", !gradientToggle.checked);
    updateAngleVisibility();
    updateNoiseVisibility();
    refreshPreview();
});


/* ----------------------------------------------------
   TEAM DROPDOWN POPULATION
---------------------------------------------------- */

let searchBoxRef = null;

fetch("/teams")
    .then(res => res.json())
    .then(data => {
        const teams = data.teams;

        const searchBox = document.createElement("input");
        searchBox.className = "dropdown-search";
        searchBox.placeholder = "Search team...";
        dropdownList.appendChild(searchBox);
        searchBoxRef = searchBox;

        searchBox.addEventListener("click", e => e.stopPropagation());
        searchBox.addEventListener("input", () => {
            const filter = searchBox.value.toLowerCase();
            document.querySelectorAll(".dropdown-item").forEach(item => {
                item.style.display = item.dataset.team.toLowerCase().includes(filter)
                    ? "flex"
                    : "none";
            });
        });

        for (const team of teams) {
            const item = document.createElement("div");
            item.className = "dropdown-item";
            item.dataset.team = team.name;

            item.innerHTML = `
                <img src="/dropdown/${team.logo}">
                <span>${team.name}</span>
            `;

            item.addEventListener("click", async e => {
                e.stopPropagation();
                selectedTeam = team.name;

                dropdownSelected.innerHTML = `
                    <img src="/dropdown/${team.logo}">
                    ${team.name}
                `;

                await applyTeamColors(team.name);
                dropdownList.style.display = "none";
            });

            dropdownList.appendChild(item);
        }
    });


/* ----------------------------------------------------
   IMPROVED DROPDOWN UX
---------------------------------------------------- */

function openDropdown() {
    dropdownList.style.display = "block";

    if (searchBoxRef) {
        setTimeout(() => searchBoxRef.focus(), 0);
    }

    if (selectedTeam) {
        const items = dropdownList.querySelectorAll(".dropdown-item");
        for (const item of items) {
            if (item.dataset.team === selectedTeam) {
                setTimeout(() => {
                    item.scrollIntoView({ behavior: "smooth", block: "center" });
                }, 50);
                break;
            }
        }
    }
}

function closeDropdown() {
    dropdownList.style.display = "none";
}

["click", "touchstart"].forEach(evt => {
    dropdownSelected.addEventListener(evt, e => {
        e.stopPropagation();
        const isOpen = dropdownList.style.display === "block";
        isOpen ? closeDropdown() : openDropdown();
    });
});

document.addEventListener("click", closeDropdown);


/* ----------------------------------------------------
   LIVE PREVIEW LISTENERS
---------------------------------------------------- */

colorPicker.addEventListener("input", () => {
    colorHex.value = colorPicker.value;
    refreshPreview();
});

colorHex.addEventListener("input", () => {
    colorPicker.value = colorHex.value;
    refreshPreview();
});

gradColor2.addEventListener("input", () => {
    gradHex2.value = gradColor2.value;
    refreshPreview();
});

gradHex2.addEventListener("input", () => {
    gradColor2.value = gradHex2.value;
    refreshPreview();
});

gradientToggle.addEventListener("change", refreshPreview);
gradientStyle.addEventListener("change", refreshPreview);

angleSlider.addEventListener("input", () => {
    angleValue.textContent = angleSlider.value;
    refreshPreview();
});

noiseDetail.addEventListener("input", refreshPreview);


/* ----------------------------------------------------
   GENERATE BUTTON
---------------------------------------------------- */

generateBtn.onclick = async () => {
    showLoading();

    const type = typeSelect.value;

    if (!selectedTeam) {
        alert("Please select a team.");
        hideLoading();
        return;
    }

    const params = new URLSearchParams({
        team: selectedTeam,
        type,
    });

    if (stickerBombEnabled) {
        params.append("stickerbomb", "1");
    } else {
        if (gradientToggle.checked) {
            params.append("gradient_enabled", "1");
            params.append("style", gradientStyle.value);
            params.append("color1", colorPicker.value);
            params.append("color2", gradColor2.value);
            params.append("angle", angleSlider.value);

            if (gradientStyle.value === "noise") {
                params.append("noise_detail", noiseDetail.value);
            }
        } else {
            params.append("color", colorPicker.value);
        }
    }

    try {
        const res = await fetch(`/generate?${params.toString()}`);
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);

        document.getElementById("previewImage").src = url;
        document.getElementById("downloadLink").href = url;
        document.getElementById("previewSection").classList.remove("hidden");
    } catch (err) {
        console.error(err);
        alert("Error generating wallpaper.");
    } finally {
        hideLoading();
    }
};


/* ----------------------------------------------------
   UTILITIES
---------------------------------------------------- */

function shadeColor(hex, percent) {
    const num = parseInt(hex.slice(1), 16);
    const r = Math.max(0, (num >> 16) + percent);
    const g = Math.max(0, ((num >> 8) & 0x00FF) + percent);
    const b = Math.max(0, (num & 0x0000FF) + percent);
    return (
        "#" +
        ((r << 16) | (g << 8) | b)
            .toString(16)
            .padStart(6, "0")
    );
}
