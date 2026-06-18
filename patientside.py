<!DOCTYPE html>
<html lang="da">
<head>
  <meta charset="UTF-8">
  <title>Patientside</title>

  <style>
    body {
      margin: 0;
      font-family: Arial, sans-serif;
      background: #f4f4f4;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
    }

    .device {
      width: 360px;
      height: 520px;
      background: black;
      border-radius: 45px;
      border: 8px solid #9c9c9c;
      box-shadow: 0 8px 25px rgba(0,0,0,0.35);
      color: white;
      padding: 25px;
      box-sizing: border-box;
      position: relative;
      text-align: center;
    }

    h1 {
      font-size: 25px;
      margin-top: 25px;
    }

    h2 {
      font-size: 24px;
      margin: 5px 0 8px;
    }

    .selection {
      display: flex;
      justify-content: space-around;
      margin-top: 30px;
    }

    .column h3 {
      text-decoration: underline;
      font-size: 19px;
      margin-bottom: 25px;
    }

    .option {
      font-size: 20px;
      font-weight: bold;
      color: #444;
      margin: 25px 0;
      cursor: pointer;
    }

    .selected {
      color: white;
    }

    button {
      border: none;
      color: white;
      font-weight: bold;
      font-size: 16px;
      padding: 11px 16px;
      cursor: pointer;
    }

    .start, .green {
      background: #009846;
    }

    .red {
      background: #b00000;
    }

    .back {
      background: #333;
      font-size: 13px;
      padding: 7px 12px;
      margin-bottom: 8px;
      border-radius: 4px;
    }

    #startBtn {
      margin-top: 15px;
      display: none;
    }

    .hidden {
      display: none;
    }

    .measurements {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;
      margin-right: 45px;
      margin-top: 5px;
    }

    .measurement-box {
      font-size: 15px;
      font-weight: bold;
      min-height: 155px;
    }

    .measurement-box p {
      margin: 16px 0;
    }

    .empty {
      color: #333;
    }

    .labels {
      position: absolute;
      right: 25px;
      top: 205px;
      color: #0099ff;
      font-weight: bold;
      line-height: 40px;
      font-size: 15px;
    }

    .average {
      margin-top: 5px;
      font-size: 15px;
      font-weight: bold;
      min-height: 42px;
    }

    .status {
      margin-top: 8px;
      font-size: 14px;
      color: #ccc;
      min-height: 20px;
    }

    .buttons {
      display: flex;
      justify-content: center;
      gap: 12px;
      margin-top: 14px;
    }

    .home-button {
      width: 45px;
      height: 45px;
      background: #222;
      border-radius: 50%;
      position: absolute;
      bottom: 18px;
      left: 50%;
      transform: translateX(-50%);
    }
  </style>
</head>

<body>

  <div class="device">

    <!-- SIDE 1 -->
    <div id="page1">
      <h1>Velkommen</h1>

      <div class="selection">
        <div class="column">
          <h3>Vælg dag</h3>
          <div class="option day" onclick="selectDay(this)">Dag 1</div>
          <div class="option day" onclick="selectDay(this)">Dag 2</div>
          <div class="option day" onclick="selectDay(this)">Dag 3</div>
        </div>

        <div class="column">
          <h3>Vælg tidspunkt</h3>
          <div class="option time" onclick="selectTime(this)">Morgen</div>
          <div class="option time" onclick="selectTime(this)">Aften</div>
        </div>
      </div>

      <button id="startBtn" class="start" onclick="startPage()">
        START MÅLING
      </button>
    </div>

    <!-- SIDE 2 -->
    <div id="page2" class="hidden">
      <h2 id="title">Dag 1<br>Morgen</h2>

      <button class="back" onclick="goBack()">← Tilbage</button>

      <div class="measurements">
        <div class="measurement-box">
          <p>1. måling</p>
          <div id="m1" class="empty">
            <p>-</p>
            <p>-</p>
            <p>-</p>
          </div>
        </div>

        <div class="measurement-box">
          <p>2. måling</p>
          <div id="m2" class="empty">
            <p>-</p>
            <p>-</p>
            <p>-</p>
          </div>
        </div>

        <div class="measurement-box">
          <p>3. måling</p>
          <div id="m3" class="empty">
            <p>-</p>
            <p>-</p>
            <p>-</p>
          </div>
        </div>
      </div>

      <div class="labels">
        SYS<br>
        DIA<br>
        PULS
      </div>

      <div id="average" class="average">
        Gennemsnit<br>
        (...)
      </div>

      <div class="status" id="statusText">
        Klar til første måling
      </div>

      <div class="buttons">
        <button id="measureBtn" class="green" onclick="takeMeasurement()">
          Tag måling
        </button>

        <button id="againBtn" class="red hidden" onclick="resetMeasurements()">
          Mål igen
        </button>

        <button id="sendBtn" class="green hidden" onclick="sendToDoctor()">
          Send til læge
        </button>
      </div>
    </div>

    <div class="home-button"></div>
  </div>

  <script>
    let selectedDay = "";
    let selectedTime = "";
    let measurementIndex = 0;

    const fakeMeasurements = [
      { sys: 128, dia: 83, puls: 69 },
      { sys: 126, dia: 81, puls: 71 },
      { sys: 122, dia: 77, puls: 65 }
    ];

    function selectDay(element) {
      document.querySelectorAll(".day").forEach(day => {
        day.classList.remove("selected");
      });

      element.classList.add("selected");
      selectedDay = element.innerText;
      checkSelection();
    }

    function selectTime(element) {
      document.querySelectorAll(".time").forEach(time => {
        time.classList.remove("selected");
      });

      element.classList.add("selected");
      selectedTime = element.innerText;
      checkSelection();
    }

    function checkSelection() {
      if (selectedDay !== "" && selectedTime !== "") {
        document.getElementById("startBtn").style.display = "inline-block";
      }
    }

    function startPage() {
      resetMeasurements();

      document.getElementById("page1").classList.add("hidden");
      document.getElementById("page2").classList.remove("hidden");

      document.getElementById("title").innerHTML =
        selectedDay + "<br>" + selectedTime;
    }

    function takeMeasurement() {
      if (measurementIndex >= 3) return;

      document.getElementById("statusText").innerText = "Måler...";

      setTimeout(() => {
        const data = fakeMeasurements[measurementIndex];
        const boxId = "m" + (measurementIndex + 1);

        document.getElementById(boxId).classList.remove("empty");
        document.getElementById(boxId).innerHTML = `
          <p>${data.sys}</p>
          <p>${data.dia}</p>
          <p>${data.puls}</p>
        `;

        measurementIndex++;

        if (measurementIndex < 3) {
          document.getElementById("statusText").innerText =
            "Måling " + measurementIndex + " gemt. Tag næste måling.";
        } else {
          calculateAverage();
          document.getElementById("statusText").innerText =
            "Alle målinger er færdige.";
          document.getElementById("measureBtn").classList.add("hidden");
          document.getElementById("againBtn").classList.remove("hidden");
          document.getElementById("sendBtn").classList.remove("hidden");
        }
      }, 1000);
    }

    function calculateAverage() {
      let sysAvg = Math.round((128 + 126 + 122) / 3);
      let diaAvg = Math.round((83 + 81 + 77) / 3);
      let pulsAvg = Math.round((69 + 71 + 65) / 3);

      document.getElementById("average").innerHTML = `
        Gennemsnit<br>
        SYS: ${sysAvg} &nbsp; DIA: ${diaAvg} &nbsp; PULS: ${pulsAvg}
      `;
    }

    function resetMeasurements() {
      measurementIndex = 0;

      for (let i = 1; i <= 3; i++) {
        document.getElementById("m" + i).classList.add("empty");
        document.getElementById("m" + i).innerHTML = `
          <p>-</p>
          <p>-</p>
          <p>-</p>
        `;
      }

      document.getElementById("average").innerHTML = `
        Gennemsnit<br>
        (...)
      `;

      document.getElementById("statusText").innerText = "Klar til første måling";
      document.getElementById("measureBtn").classList.remove("hidden");
      document.getElementById("againBtn").classList.add("hidden");
      document.getElementById("sendBtn").classList.add("hidden");
    }

    function goBack() {
      resetMeasurements();

      document.getElementById("page2").classList.add("hidden");
      document.getElementById("page1").classList.remove("hidden");
    }

    function sendToDoctor() {
      alert("Målingerne er sendt til lægen.");
    }
  </script>

</body>
</html>