const moviesObject = {
    "☕🍵": "Java",
    // "🐍🔡": "Python",
    // "🌐📄": "HTML",
    // "☕📜": "JavaScript",
    // "⚙️🐧": "C",
    // "🖥️🏁": "C++",
    // "🍵👑": "Kotlin",
    // "📱🎨": "Swift",
    // "🔗📚": "C#",
    // "🌟🎛️": "Ruby",
    // "🚀🛠️": "Rust",
    // "🎨📄": "CSS",
    // "👟🐘": "PHP",
    // "🔄📄": "TypeScript",
    // "📱🔗": "ReactNative",
    // "🧑‍🔬⚙️": "MATLAB",
    // "📝🔍": "Perl",
    // "🌈📋": "Dart",
    // "🐬📘": "Go",
    // "💻📑": "SQL"
};

src = "https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"

const container = document.querySelector(".container");
const controls = document.querySelector(".controls-container");
const startButton = document.getElementById("start");
const letterContainer = document.getElementById("letter-container");
const userInputSection = document.getElementById("userInputSection");
const resultText = document.getElementById("result");
const hints = Object.keys(moviesObject);
const specialCharacters = "#+";
let randomHint = "",
  randomWord = "";
let winCount = 0,
  lossCount = 5;

const generateRandomValue = (array) => Math.floor(Math.random() * array.length);

// Blocker
const blocker = () => {
  let letterButtons = document.querySelectorAll(".letters");
  letterButtons.forEach((button) => {
    button.disabled = true;
  });
  stopGame();
};

// Start game
startButton.addEventListener("click", () => {
  // Controls and buttons visibility
  controls.classList.add("hide");
  init();
});

// Stop Game
const stopGame = () => {
  controls.classList.remove("hide");
};

// Generate Word
const generateWord = () => {
  letterContainer.classList.remove("hide");
  userInputSection.innerText = "";
  randomHint = hints[generateRandomValue(hints)];
  randomWord = moviesObject[randomHint];
  container.innerHTML = `<div id="movieHint">${randomHint}</div>`;
  let displayItem = "";
  randomWord.split("").forEach((value) => {
    if (value == " ") {
      winCount += 1;
      displayItem += `<span class="inputSpace">&nbsp;</span>`;
    } else {
      displayItem += `<span class="inputSpace">_</span>`;
    }
  });
  userInputSection.innerHTML = displayItem;
};

// Initial Function
const init = () => {
  winCount = 0;
  lossCount = 8;
  document.getElementById(
    "chanceCount"
  ).innerHTML = `<span>Jogadas restantes: ${lossCount}</span>`;
  randomHint = null;
  randomWord = "";
  userInputSection.innerHTML = "";
  letterContainer.classList.add("hide");
  letterContainer.innerHTML = "";
  generateWord();

  for (let i = 65; i < 91; i++) {
    let button = document.createElement("button");
    button.classList.add("letters");
    // Número para ASCII [A - Z]
    button.innerText = String.fromCharCode(i);
    addClickListener(button, randomWord);
    letterContainer.appendChild(button);
  }

  // Adicione caracteres especiais
  specialCharacters.split('').forEach(char => {
    let button = document.createElement("button");
    button.classList.add("letters");
    button.innerText = char;
    addClickListener(button, randomWord);
    letterContainer.appendChild(button);
  });
};

const addClickListener = (button, word) => {
  button.addEventListener("click", () => {
    let charArray = word.toUpperCase().split("");
    let inputSpace = document.getElementsByClassName("inputSpace");
    if (charArray.includes(button.innerText)) {
      charArray.forEach((char, index) => {
        if (char === button.innerText) {
          button.classList.add("used");
          inputSpace[index].innerText = char;
          winCount += 1;
          if (winCount == charArray.length) {
            resultText.innerHTML = `<div class='message'><h2 class='win-msg'>Você venceu!</h2></div>`;
            resultText.classList.add("text-sucess");
            shoot();
            console.log("Chamando updateScore...");
            getUserId().then(userId => {
                console.log("UserId obtido:", userId);
                updateScore(userId, 100);
            }).catch(error => {
                console.error("Erro ao obter userId:", error);
            });
            blocker();
          }
        }
      });
    } else {
      resultText.classList.remove("text-sucess");
      resultText.classList.add("text-error");
      lossCount -= 1;
      document.getElementById(
        "chanceCount"
      ).innerHTML = `<span>Jogadas restantes:</span> ${lossCount}`;
      button.classList.add("used");
      if (lossCount == 0) {
        resultText.innerHTML = `<div class='message'><h2 class='lose-msg'>Você perdeu!</h2></div>`;
        blocker();
      }
    }
    button.disabled = true;
  });
}

window.onload = () => {
  init();
};

// Confetti animaton

function shoot() {

  var defaults = {
    spread: 360,
    ticks: 100,
    gravity: 0,
    decay: 1,
    startVelocity: 10,
    colors: ['FFE400', 'FFBD00', 'E89400', 'FFCA6C', 'FDFFB8']
  };

  confetti({
    ...defaults,
    particleCount: 30,
    scalar: 1.5,
    shapes: ['star']
  });

  confetti({
    ...defaults,
    particleCount: 10,
    scalar: 1,
    shapes: ['circle']
  });
}

// Codigo novo!!!

// pegando o endpoint do update score do backend
async function updateScore(pointsEarned) {
  try {
      const response = await fetch(`/update_score/`, {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCSRFToken()
          },
          body: JSON.stringify({ points_earned: pointsEarned })
      });
      
      const data = await response.json();
      
      if (response.ok) {
          document.getElementById('points').innerText = data.points;
          document.getElementById('level').innerText = data.level;
          alert(`Parabéns! Você alcançou o nível ${data.level}`);
      } else {
          console.error("Erro ao atualizar pontuação:", data);
      }
  } catch (error) {
      console.error("Erro na requisição:", error);
  }
}

function getCSRFToken() {
return document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken'))
    .split('=')[1];
}

// Esse codigo tem que ser colocado após terminar a fase, ou mudar ele para colocar em determinada parte quando queira que adicione pontos...
// function onLevelComplete() {
//   const pointsEarned = 100;
//   const userId = getUserId();

//   updateScore(userId, pointsEarned);
// }