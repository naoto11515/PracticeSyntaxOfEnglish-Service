// start button click event handler
const numberquestions = document.getElementById("numberquestions");
const levelCategorySelect = document.getElementById("levelCategorySelect");
const levelSelect = document.getElementById("levelSelect");
const startButton = document.getElementById("startButton");

// level master data
const levelDataInitial = {value: "0", text: "-- レベルを選択してください --"};
const levelData = {
  1: [{value: "1", text: "A1"}, 
      {value: "2", text: "A2"},
      {value: "3", text: "B1"},
      {value: "4", text: "B2"},
      {value: "5", text: "C1"},
      {value: "6", text: "C2"}
    ], // CEFR levels
  2: [{value: "1", text: "5.0"},
      {value: "2", text: "6.0"},
      {value: "3", text: "7.0"},
      {value: "4", text: "8.0"},
      {value: "5", text: "9.0"}
    ], // IELTS levels
  3: [{value: "1", text: "500"},
      {value: "2", text: "600"},
      {value: "3", text: "700"},
      {value: "4", text: "800"},
      {value: "5", text: "900"}
    ], // TOEIC levels
};

levelCategorySelect.addEventListener("change", () => {
  const selectedCategory = levelCategorySelect.value;
  
  // Clear previous options
  levelSelect.innerHTML = "0"; 

  // Inithialize the level select with the default option
  const option = document.createElement("option");
  option.value = levelDataInitial.value; 
  option.textContent = levelDataInitial.text;
  levelSelect.appendChild(option);

  if (selectedCategory === "0") {
    return; // No category selected, do nothing
  }

  const levels = levelData[selectedCategory];

  levels.forEach(level => {
    const option = document.createElement("option");
    option.value = level.value;
    option.textContent = level.text;
    levelSelect.appendChild(option);
  });
});

startButton.addEventListener("click", async () => {
  const formData = new FormData();
  formData.append("numberquestions", numberquestions.value);
  formData.append("levelCategory", levelCategorySelect.value);
  formData.append("level", levelSelect.value);

  const response = await fetch("/start", {
    method: "POST",
    body: formData
  });

  const result = await response.json();

  if (!result.success) {
      alert(result.message);
  } else {
      window.location.href = result.next;
  }
});