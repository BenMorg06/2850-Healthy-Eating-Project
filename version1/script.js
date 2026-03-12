const todayStr = new Date().toISOString().slice(0, 10);

/* ---------- auth page logic ---------- */
const loginTab = document.getElementById("loginTab");
const registerTab = document.getElementById("registerTab");
const loginForm = document.getElementById("loginForm");
const registerForm = document.getElementById("registerForm");

if (loginTab && registerTab && loginForm && registerForm) {
    loginTab.addEventListener("click", () => {
        loginTab.classList.add("active");
        registerTab.classList.remove("active");
        loginForm.classList.add("active");
        registerForm.classList.remove("active");
    });

    registerTab.addEventListener("click", () => {
        registerTab.classList.add("active");
        loginTab.classList.remove("active");
        registerForm.classList.add("active");
        loginForm.classList.remove("active");
    });

    loginForm.addEventListener("submit", (e) => {
        e.preventDefault();
        alert("Login form submitted. Later this can be connected to Flask.");
        window.location.href = "index.html";
    });

    registerForm.addEventListener("submit", (e) => {
        e.preventDefault();

        const password = document.getElementById("regPassword").value.trim();
        const confirmPassword = document.getElementById("regConfirmPassword").value.trim();

        if (password !== confirmPassword) {
            alert("Passwords do not match.");
            return;
        }

        alert("Register form submitted. Later this can be connected to Flask.");
        window.location.href = "index.html";
    });
}

/* ---------- main page logic ---------- */
const pages = document.querySelectorAll(".page");
const sideButtons = document.querySelectorAll(".side-btn");

const diaryEntries = document.getElementById("diaryEntries");
const diarySummary = document.getElementById("diarySummary");
const clientList = document.getElementById("clientList");
const professionalFoodList = document.getElementById("professionalFoodList");
const recommendedGrid = document.getElementById("recommendedGrid");
const favouriteGrid = document.getElementById("favouriteGrid");

const currentUser = {
    id: "client-1",
    name: "Jessie Kim"
};

const foodDatabase = [{
        id: "food-1",
        name: "Fresh Salad",
        per100g: { calories: 85, protein: 2.1, carbs: 8.5, fat: 3.2 },
        category: "Vegetable",
        img: "https://picsum.photos/seed/f1/300/200"
    },
    {
        id: "food-2",
        name: "Fruit Bowl",
        per100g: { calories: 72, protein: 1.1, carbs: 16.8, fat: 0.4 },
        category: "Fruit",
        img: "https://picsum.photos/seed/f2/300/200"
    },
    {
        id: "food-3",
        name: "Chicken Breast",
        per100g: { calories: 165, protein: 31, carbs: 0, fat: 3.6 },
        category: "Protein",
        img: "https://picsum.photos/seed/f3/300/200"
    },
    {
        id: "food-4",
        name: "Yogurt Cup",
        per100g: { calories: 95, protein: 5.2, carbs: 11.3, fat: 2.7 },
        category: "Snack",
        img: "https://picsum.photos/seed/f4/300/200"
    },
    {
        id: "food-5",
        name: "Avocado Toast",
        per100g: { calories: 182, protein: 5.4, carbs: 19.2, fat: 8.1 },
        category: "Breakfast",
        img: "https://picsum.photos/seed/f5/300/200"
    },
    {
        id: "food-6",
        name: "Healthy Soup",
        per100g: { calories: 54, protein: 2.8, carbs: 7.2, fat: 1.4 },
        category: "Soup",
        img: "https://picsum.photos/seed/f6/300/200"
    }
];

const clients = [
    { id: "client-1", name: "Jessie Kim", status: "Active today" },
    { id: "client-2", name: "Lucas Chen", status: "Needs monitoring" },
    { id: "client-3", name: "Emily Park", status: "Good progress" }
];

let selectedClientId = "client-1";
let quickAddFoodId = null;

const initialDiaryRecords = [{
        id: randomId(),
        clientId: "client-1",
        date: todayStr,
        type: "database",
        foodId: "food-3",
        name: "Chicken Breast",
        grams: 150,
        calories: 248,
        protein: 46.5,
        carbs: 0,
        fat: 5.4,
        category: "Protein",
        img: "https://picsum.photos/seed/f3/300/200"
    },
    {
        id: randomId(),
        clientId: "client-2",
        date: todayStr,
        type: "database",
        foodId: "food-1",
        name: "Fresh Salad",
        grams: 220,
        calories: 187,
        protein: 4.6,
        carbs: 18.7,
        fat: 7,
        category: "Vegetable",
        img: "https://picsum.photos/seed/f1/300/200"
    },
    {
        id: randomId(),
        clientId: "client-3",
        date: todayStr,
        type: "database",
        foodId: "food-5",
        name: "Avocado Toast",
        grams: 140,
        calories: 254.8,
        protein: 7.6,
        carbs: 26.9,
        fat: 11.3,
        category: "Breakfast",
        img: "https://picsum.photos/seed/f5/300/200"
    }
];

const initialFavouriteIds = ["food-3", "food-5"];

const initialNotes = [{
    id: randomId(),
    clientId: "client-1",
    author: "Professional",
    message: "Please keep dinner lighter today and reduce oily sauces.",
    date: todayStr,
    readByClient: false
}];

function randomId() {
    return Math.random().toString(36).slice(2, 10);
}

function round1(value) {
    return Math.round(value * 10) / 10;
}

if (sideButtons.length > 0) {
    function showPage(pageId) {
        pages.forEach(page => page.classList.toggle("active", page.id === pageId));
        sideButtons.forEach(btn => btn.classList.toggle("active", btn.dataset.page === pageId));
    }

    sideButtons.forEach(btn => {
        btn.addEventListener("click", () => showPage(btn.dataset.page));
    });

    function getStoredDiaryRecords() {
        const raw = localStorage.getItem("healthy_diary_records_v3");
        if (raw) return JSON.parse(raw);
        localStorage.setItem("healthy_diary_records_v3", JSON.stringify(initialDiaryRecords));
        return [...initialDiaryRecords];
    }

    function saveDiaryRecords(list) {
        localStorage.setItem("healthy_diary_records_v3", JSON.stringify(list));
    }

    function getStoredFavouriteIds() {
        const raw = localStorage.getItem("healthy_favourite_ids_v1");
        if (raw) return JSON.parse(raw);
        localStorage.setItem("healthy_favourite_ids_v1", JSON.stringify(initialFavouriteIds));
        return [...initialFavouriteIds];
    }

    function saveFavouriteIds(list) {
        localStorage.setItem("healthy_favourite_ids_v1", JSON.stringify(list));
    }

    function getStoredNotes() {
        const raw = localStorage.getItem("healthy_pro_notes_v3");
        if (raw) return JSON.parse(raw);
        localStorage.setItem("healthy_pro_notes_v3", JSON.stringify(initialNotes));
        return [...initialNotes];
    }

    function saveNotes(list) {
        localStorage.setItem("healthy_pro_notes_v3", JSON.stringify(list));
    }

    function calculateNutrition(per100g, grams) {
        const factor = grams / 100;
        return {
            calories: round1(per100g.calories * factor),
            protein: round1(per100g.protein * factor),
            carbs: round1(per100g.carbs * factor),
            fat: round1(per100g.fat * factor)
        };
    }

    function findFoodByName(name) {
        return foodDatabase.find(item => item.name.toLowerCase() === name.trim().toLowerCase());
    }

    function findFoodById(id) {
        return foodDatabase.find(item => item.id === id);
    }

    function getDiaryRecordsByClientAndDate(clientId, date) {
        return getStoredDiaryRecords().filter(item => item.clientId === clientId && item.date === date);
    }

    function sumNutrition(records) {
        return records.reduce((acc, item) => {
            acc.calories += Number(item.calories) || 0;
            acc.protein += Number(item.protein) || 0;
            acc.carbs += Number(item.carbs) || 0;
            acc.fat += Number(item.fat) || 0;
            return acc;
        }, { calories: 0, protein: 0, carbs: 0, fat: 0 });
    }

    function setDefaultDates() {
        const foodDate = document.getElementById("foodDate");
        const recipeDate = document.getElementById("recipeDate");
        const diaryDateFilter = document.getElementById("diaryDateFilter");
        const professionalDateFilter = document.getElementById("professionalDateFilter");
        const quickAddDate = document.getElementById("quickAddDate");

        if (foodDate) foodDate.value = todayStr;
        if (recipeDate) recipeDate.value = todayStr;
        if (diaryDateFilter) diaryDateFilter.value = todayStr;
        if (professionalDateFilter) professionalDateFilter.value = todayStr;
        if (quickAddDate) quickAddDate.value = todayStr;
    }

    function isFavourite(foodId) {
        return getStoredFavouriteIds().includes(foodId);
    }

    function toggleFavourite(foodId) {
        const ids = getStoredFavouriteIds();
        const exists = ids.includes(foodId);
        const next = exists ? ids.filter(id => id !== foodId) : [foodId, ...ids];
        saveFavouriteIds(next);
        renderRecommendedFoods();
        renderFavouriteFoods();
    }

    function addFoodToDiaryFromDatabase(food, grams, date, clientId = currentUser.id) {
        const nutrition = calculateNutrition(food.per100g, grams);
        const records = getStoredDiaryRecords();

        records.unshift({
            id: randomId(),
            clientId,
            date,
            type: "database",
            foodId: food.id,
            name: food.name,
            grams,
            calories: nutrition.calories,
            protein: nutrition.protein,
            carbs: nutrition.carbs,
            fat: nutrition.fat,
            category: food.category,
            img: food.img
        });

        saveDiaryRecords(records);
    }

    function renderFoodCard(food, fromFavourite = false) {
        const liked = isFavourite(food.id);

        return `
      <div class="menu-card">
        <img src="${food.img}" alt="${food.name}">
        <h4>${food.name}</h4>
        <p>${food.category}</p>
        <div class="macro-row">
          <span>${food.per100g.calories} kcal / 100g</span>
          <span>P ${food.per100g.protein}g</span>
          <span>C ${food.per100g.carbs}g</span>
          <span>F ${food.per100g.fat}g</span>
        </div>
        <div class="card-action-row">
          <button class="like-btn" data-food-id="${food.id}" type="button">
            ${liked ? "♥ Liked" : "♡ Like"}
          </button>
          <button class="quick-btn" data-food-id="${food.id}" data-source="${fromFavourite ? "favourite" : "menu"}" type="button">
            Quick Add
          </button>
        </div>
      </div>
    `;
    }

    function bindFoodCardActions() {
        document.querySelectorAll(".like-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                toggleFavourite(btn.dataset.foodId);
            });
        });

        document.querySelectorAll(".quick-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                openQuickAddModal(btn.dataset.foodId);
            });
        });
    }

    function renderRecommendedFoods() {
        if (!recommendedGrid) return;
        recommendedGrid.innerHTML = foodDatabase.map(food => renderFoodCard(food, false)).join("");
        bindFoodCardActions();
    }

    function renderFavouriteFoods() {
        if (!favouriteGrid) return;
        const favouriteIds = getStoredFavouriteIds();
        const favouriteFoods = foodDatabase.filter(food => favouriteIds.includes(food.id));

        if (!favouriteFoods.length) {
            favouriteGrid.innerHTML = `<div class="empty-state">No favourite foods yet.</div>`;
            return;
        }

        favouriteGrid.innerHTML = favouriteFoods.map(food => renderFoodCard(food, true)).join("");
        bindFoodCardActions();
    }

    function renderDiary() {
        if (!diaryEntries || !diarySummary) return;
        const selectedDate = document.getElementById("diaryDateFilter").value || todayStr;
        const records = getDiaryRecordsByClientAndDate(currentUser.id, selectedDate);
        const totals = sumNutrition(records);

        diarySummary.innerHTML = `
      <div class="diary-summary-box">
        <strong>${round1(totals.calories)} kcal</strong>
        <span>Calories</span>
      </div>
      <div class="diary-summary-box">
        <strong>${round1(totals.protein)} g</strong>
        <span>Protein</span>
      </div>
      <div class="diary-summary-box">
        <strong>${round1(totals.carbs)} g</strong>
        <span>Carbs</span>
      </div>
      <div class="diary-summary-box">
        <strong>${round1(totals.fat)} g</strong>
        <span>Fat</span>
      </div>
    `;

        if (!records.length) {
            diaryEntries.innerHTML = `<div class="empty-state">No diary food records for this date.</div>`;
            return;
        }

        diaryEntries.innerHTML = records.map(item => `
      <div class="diary-entry">
        <h4>${item.name}</h4>
        <div class="meta">${item.date} · ${item.grams} g · ${item.category}</div>
        <p>Calories: ${item.calories} kcal</p>
        <p>Protein: ${item.protein} g · Carbs: ${item.carbs} g · Fat: ${item.fat} g</p>
        ${item.ingredients ? `<p>Recipe: ${item.ingredients}</p>` : ""}
      </div>
    `).join("");
  }

  function renderClients() {
    if (!clientList) return;
    clientList.innerHTML = clients.map(client => `
      <div class="client-item ${client.id === selectedClientId ? "active" : ""}" data-id="${client.id}">
        <h4>${client.name}</h4>
        <p>${client.status}</p>
      </div>
    `).join("");

    document.querySelectorAll(".client-item").forEach(item => {
      item.addEventListener("click", () => {
        selectedClientId = item.dataset.id;
        renderClients();
        renderProfessional();
        renderProBell();
      });
    });
  }

  function setBarHeight(elementId, value, maxValue) {
    const el = document.getElementById(elementId);
    if (!el) return;
    const pct = maxValue <= 0 ? 30 : Math.max(18, Math.min(100, (value / maxValue) * 100));
    el.style.height = `${pct}%`;
  }

  function renderProfessional() {
    if (!professionalFoodList) return;

    const selectedDate = document.getElementById("professionalDateFilter").value || todayStr;
    const client = clients.find(c => c.id === selectedClientId);
    const records = getDiaryRecordsByClientAndDate(selectedClientId, selectedDate);
    const totals = sumNutrition(records);

    const proClientName = document.getElementById("proClientName");
    const proClientStatus = document.getElementById("proClientStatus");
    const clientCalories = document.getElementById("clientCalories");
    const clientProtein = document.getElementById("clientProtein");
    const clientCarbs = document.getElementById("clientCarbs");
    const clientFat = document.getElementById("clientFat");

    if (proClientName) proClientName.textContent = client ? client.name : "Client";
    if (proClientStatus) proClientStatus.textContent = `Dietary record for ${selectedDate}`;
    if (clientCalories) clientCalories.textContent = `${round1(totals.calories)} kcal`;
    if (clientProtein) clientProtein.textContent = `${round1(totals.protein)} g`;
    if (clientCarbs) clientCarbs.textContent = `${round1(totals.carbs)} g`;
    if (clientFat) clientFat.textContent = `${round1(totals.fat)} g`;

    if (!records.length) {
      professionalFoodList.innerHTML = `<div class="empty-state">No food records for this client on the selected date.</div>`;
    } else {
      professionalFoodList.innerHTML = records.map(item => `
        <div class="professional-food-item">
          <h4>${item.name}</h4>
          <p>${item.date} · ${item.grams} g · ${item.calories} kcal</p>
          <p>Protein ${item.protein} g · Carbs ${item.carbs} g · Fat ${item.fat} g</p>
          ${item.ingredients ? `<p>Recipe: ${item.ingredients}</p>` : ""}
        </div>
      `).join("");
    }

    const maxMacro = Math.max(totals.protein, totals.carbs, totals.fat, 1);
    setBarHeight("proProteinBar", totals.protein, maxMacro);
    setBarHeight("proCarbsBar", totals.carbs, maxMacro);
    setBarHeight("proFatBar", totals.fat, maxMacro);

    const proProteinText = document.getElementById("proProteinText");
    const proCarbsText = document.getElementById("proCarbsText");
    const proFatText = document.getElementById("proFatText");

    if (proProteinText) proProteinText.textContent = `${round1(totals.protein)}g`;
    if (proCarbsText) proCarbsText.textContent = `${round1(totals.carbs)}g`;
    if (proFatText) proFatText.textContent = `${round1(totals.fat)}g`;
  }

  function renderUserBell() {
    const countEl = document.getElementById("userBellCount");
    const list = document.getElementById("userBellList");
    if (!countEl || !list) return;

    const notes = getStoredNotes().filter(note => note.clientId === currentUser.id);
    const unreadCount = notes.filter(note => !note.readByClient).length;
    countEl.textContent = unreadCount;

    if (!notes.length) {
      list.innerHTML = `<div class="empty-state">No messages.</div>`;
      return;
    }

    list.innerHTML = notes.map(note => `
      <div class="bell-item">
        <h4>Professional Note</h4>
        <p>${note.message}</p>
        <div class="meta">${note.date}${note.readByClient ? " · Read" : " · New"}</div>
      </div>
    `).join("");
  }

  function markClientNotesAsRead() {
    const notes = getStoredNotes();
    let changed = false;
    notes.forEach(note => {
      if (note.clientId === currentUser.id && !note.readByClient) {
        note.readByClient = true;
        changed = true;
      }
    });
    if (changed) {
      saveNotes(notes);
      renderUserBell();
    }
  }

  function renderProBell() {
    const countEl = document.getElementById("proBellCount");
    const list = document.getElementById("proBellList");
    if (!countEl || !list) return;

    const notes = getStoredNotes().filter(note => note.clientId === selectedClientId);
    countEl.textContent = notes.length;

    if (!notes.length) {
      list.innerHTML = `<div class="empty-state">No notes for this client.</div>`;
      return;
    }

    list.innerHTML = notes.map(note => `
      <div class="bell-item">
        <h4>Professional Note</h4>
        <p>${note.message}</p>
        <div class="meta">${note.date}</div>
      </div>
    `).join("");
  }

  function togglePanel(panelId) {
    const panel = document.getElementById(panelId);
    if (panel) panel.classList.toggle("hidden");
  }

  function hidePanel(panelId) {
    const panel = document.getElementById(panelId);
    if (panel) panel.classList.add("hidden");
  }

  const foodLookupTab = document.getElementById("foodLookupTab");
  const manualRecipeTab = document.getElementById("manualRecipeTab");
  const foodLookupPanel = document.getElementById("foodLookupPanel");
  const manualRecipePanel = document.getElementById("manualRecipePanel");
  const foodLookupResult = document.getElementById("foodLookupResult");

  function activateLookupMode() {
    if (!foodLookupTab || !manualRecipeTab || !foodLookupPanel || !manualRecipePanel) return;
    foodLookupTab.classList.add("active");
    manualRecipeTab.classList.remove("active");
    foodLookupPanel.classList.add("active");
    manualRecipePanel.classList.remove("active");
  }

  function activateManualMode() {
    if (!foodLookupTab || !manualRecipeTab || !foodLookupPanel || !manualRecipePanel) return;
    manualRecipeTab.classList.add("active");
    foodLookupTab.classList.remove("active");
    manualRecipePanel.classList.add("active");
    foodLookupPanel.classList.remove("active");
  }

  if (foodLookupTab && manualRecipeTab) {
    foodLookupTab.addEventListener("click", activateLookupMode);
    manualRecipeTab.addEventListener("click", activateManualMode);
  }

  const checkFoodBtn = document.getElementById("checkFoodBtn");
  if (checkFoodBtn) {
    checkFoodBtn.addEventListener("click", () => {
      const name = document.getElementById("foodName").value.trim();
      const gramsValue = document.getElementById("foodGrams").value.trim();

      if (!name || !gramsValue) {
        if (foodLookupResult) foodLookupResult.innerHTML = `Please enter both food name and grams.`;
        return;
      }

      const grams = Number(gramsValue);
      const food = findFoodByName(name);

      if (!food) {
        if (foodLookupResult) {
          foodLookupResult.innerHTML = `
            Food not found in database.<br>
            Please use <strong>Manual Recipe Entry</strong> to enter your own recipe and nutrition values.
          `;
        }
        return;
      }

      const nutrition = calculateNutrition(food.per100g, grams);
      if (foodLookupResult) {
        foodLookupResult.innerHTML = `
          <strong>Found:</strong> ${food.name}<br>
          ${grams} g · ${nutrition.calories} kcal<br>
          Protein ${nutrition.protein} g · Carbs ${nutrition.carbs} g · Fat ${nutrition.fat} g
        `;
      }
    });
  }

  const addFoodBtn = document.getElementById("addFoodBtn");
  if (addFoodBtn) {
    addFoodBtn.addEventListener("click", () => {
      const date = document.getElementById("foodDate").value || todayStr;
      const name = document.getElementById("foodName").value.trim();
      const gramsValue = document.getElementById("foodGrams").value.trim();

      if (!name || !gramsValue) {
        alert("Please enter date, food name and grams.");
        return;
      }

      const grams = Number(gramsValue);
      const food = findFoodByName(name);

      if (!food) {
        alert("Food not found in database. Please use Manual Recipe Entry.");
        activateManualMode();
        return;
      }

      addFoodToDiaryFromDatabase(food, grams, date, currentUser.id);
      renderDiary();
      renderProfessional();

      if (foodLookupResult) {
        foodLookupResult.innerHTML = `
          <strong>Record added successfully.</strong><br>
          ${food.name} · ${grams} g · ${calculateNutrition(food.per100g, grams).calories} kcal
        `;
      }

      document.getElementById("foodName").value = "";
      document.getElementById("foodGrams").value = "";
    });
  }

  const saveRecipeBtn = document.getElementById("saveRecipeBtn");
  if (saveRecipeBtn) {
    saveRecipeBtn.addEventListener("click", () => {
      const date = document.getElementById("recipeDate").value || todayStr;
      const name = document.getElementById("recipeName").value.trim();
      const grams = document.getElementById("recipeGrams").value.trim();
      const category = document.getElementById("recipeCategory").value.trim() || "Manual Recipe";
      const ingredients = document.getElementById("recipeIngredients").value.trim();
      const calories = document.getElementById("recipeCalories").value.trim();
      const protein = document.getElementById("recipeProtein").value.trim();
      const carbs = document.getElementById("recipeCarbs").value.trim();
      const fat = document.getElementById("recipeFat").value.trim();

      if (!name || !grams || !ingredients || !calories || !protein || !carbs || !fat) {
        alert("Please complete all manual recipe fields.");
        return;
      }

      const records = getStoredDiaryRecords();
      records.unshift({
        id: randomId(),
        clientId: currentUser.id,
        date,
        type: "manual",
        name,
        grams: Number(grams),
        calories: Number(calories),
        protein: Number(protein),
        carbs: Number(carbs),
        fat: Number(fat),
        category,
        img: `https://picsum.photos/seed/${encodeURIComponent(name)}/300/200`,
        ingredients
      });

      saveDiaryRecords(records);
      renderDiary();
      renderProfessional();

      document.getElementById("recipeName").value = "";
      document.getElementById("recipeGrams").value = "";
      document.getElementById("recipeCategory").value = "";
      document.getElementById("recipeIngredients").value = "";
      document.getElementById("recipeCalories").value = "";
      document.getElementById("recipeProtein").value = "";
      document.getElementById("recipeCarbs").value = "";
      document.getElementById("recipeFat").value = "";

      alert("Manual recipe saved successfully.");
    });
  }

  function openQuickAddModal(foodId) {
    quickAddFoodId = foodId;
    const food = findFoodById(foodId);
    const quickAddTitle = document.getElementById("quickAddTitle");
    const quickAddDate = document.getElementById("quickAddDate");
    const quickAddGrams = document.getElementById("quickAddGrams");
    const quickAddModal = document.getElementById("quickAddModal");

    if (quickAddTitle) quickAddTitle.textContent = `Quick Add - ${food ? food.name : "Food"}`;
    if (quickAddDate) quickAddDate.value = todayStr;
    if (quickAddGrams) quickAddGrams.value = "";
    if (quickAddModal) quickAddModal.classList.remove("hidden");
  }

  function closeQuickAddModal() {
    quickAddFoodId = null;
    const modal = document.getElementById("quickAddModal");
    if (modal) modal.classList.add("hidden");
  }

  const closeQuickAddModalBtn = document.getElementById("closeQuickAddModal");
  if (closeQuickAddModalBtn) {
    closeQuickAddModalBtn.addEventListener("click", closeQuickAddModal);
  }

  const confirmQuickAddBtn = document.getElementById("confirmQuickAddBtn");
  if (confirmQuickAddBtn) {
    confirmQuickAddBtn.addEventListener("click", () => {
      if (!quickAddFoodId) return;

      const food = findFoodById(quickAddFoodId);
      const date = document.getElementById("quickAddDate").value || todayStr;
      const grams = Number(document.getElementById("quickAddGrams").value);

      if (!food || !grams || grams <= 0) {
        alert("Please enter valid grams.");
        return;
      }

      addFoodToDiaryFromDatabase(food, grams, date, currentUser.id);
      renderDiary();
      renderProfessional();
      closeQuickAddModal();
      alert("Food added to diary.");
    });
  }

  const diaryDateFilter = document.getElementById("diaryDateFilter");
  if (diaryDateFilter) diaryDateFilter.addEventListener("change", renderDiary);

  const professionalDateFilter = document.getElementById("professionalDateFilter");
  if (professionalDateFilter) professionalDateFilter.addEventListener("change", renderProfessional);

  const todayDiaryBtn = document.getElementById("todayDiaryBtn");
  if (todayDiaryBtn) {
    todayDiaryBtn.addEventListener("click", () => {
      document.getElementById("diaryDateFilter").value = todayStr;
      renderDiary();
    });
  }

  const todayProfessionalBtn = document.getElementById("todayProfessionalBtn");
  if (todayProfessionalBtn) {
    todayProfessionalBtn.addEventListener("click", () => {
      document.getElementById("professionalDateFilter").value = todayStr;
      renderProfessional();
    });
  }

  const saveProNoteBtn = document.getElementById("saveProNoteBtn");
  if (saveProNoteBtn) {
    saveProNoteBtn.addEventListener("click", () => {
      const text = document.getElementById("proNoteText").value.trim();
      if (!text) {
        alert("Please enter a note.");
        return;
      }

      const notes = getStoredNotes();
      notes.unshift({
        id: randomId(),
        clientId: selectedClientId,
        author: "Professional",
        message: text,
        date: document.getElementById("professionalDateFilter").value || todayStr,
        readByClient: false
      });
      saveNotes(notes);

      document.getElementById("proNoteText").value = "";
      renderProBell();
      renderUserBell();

      alert("Note sent successfully.");
    });
  }

  const userBellBtn = document.getElementById("userBellBtn");
  if (userBellBtn) {
    userBellBtn.addEventListener("click", () => {
      togglePanel("userBellPanel");
      hidePanel("proBellPanel");
      const panel = document.getElementById("userBellPanel");
      if (panel && !panel.classList.contains("hidden")) {
        markClientNotesAsRead();
      }
    });
  }

  const proBellBtn = document.getElementById("proBellBtn");
  if (proBellBtn) {
    proBellBtn.addEventListener("click", () => {
      togglePanel("proBellPanel");
      hidePanel("userBellPanel");
    });
  }

  document.addEventListener("click", (event) => {
    const userWrap = document.getElementById("userBellWrap");
    const proWrap = document.querySelector(".pro-bell-wrap");
    const modalCard = document.querySelector(".modal-card");
    const modal = document.getElementById("quickAddModal");

    if (userWrap && !userWrap.contains(event.target)) {
      hidePanel("userBellPanel");
    }
    if (proWrap && !proWrap.contains(event.target)) {
      hidePanel("proBellPanel");
    }
    if (modal && !modal.classList.contains("hidden") && event.target === modal && modalCard && !modalCard.contains(event.target)) {
      closeQuickAddModal();
    }
  });

  setDefaultDates();
  renderRecommendedFoods();
  renderFavouriteFoods();
  renderDiary();
  renderClients();
  renderProfessional();
  renderUserBell();
  renderProBell();
  showPage("dashboard");
  activateLookupMode();
}