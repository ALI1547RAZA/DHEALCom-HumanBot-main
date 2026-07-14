<!doctype html>
<html lang="en">

<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ReplayBG Demo</title>

  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.5/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" rel="stylesheet">

  <style>
    html,
    body {
      height: 100%;
      margin: 0;
    }

    body {
      display: flex;
      flex-direction: column;
    }

    .main-container {
      flex: 1;
      display: flex;
      flex-direction: column;
    }

    .section-result {
      flex: 2;
      padding: 10px;
      display: flex;
      flex-direction: column;
    }

    .section-bottom {
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }

    .prompt-wrapper {
      flex: 1;
      padding: 10px;
    }

    .mic-wrapper {
      flex: 2;
      display: flex;
      justify-content: center;
      align-items: center;
    }

    #startBtn {
      width: 60px;
      height: 60px;
      border-radius: 50%;
      font-size: 24px;
      display: flex;
      justify-content: center;
      align-items: center;
    }

    .small-text {
      font-size: 0.85rem;
      padding: 6px;
    }
  </style>
</head>

<body>
  <div class="container-fluid main-container">
    <!-- Titolo -->
    <h1 class="text-center mt-3" id="titolo">ReplayBG Demo</h1>

    <!-- Sezione risultato -->
    <div class="section-result">
      <!-- <label for="result" class="form-label">Risultato finale</label> -->
      <div class="d-flex align-items-start mb-2 h-100">
        <!-- Icona utente -->
        <div class="me-2 d-flex justify-content-center " style="width: 40px;">
          <i class="bi bi-brilliance fs-2 text-black"></i>
        </div>
        <!-- Textarea risultato -->
        <textarea id="result" class="form-control h-100" placeholder="Risultato..." readonly></textarea>
      </div>
      <!-- Toggle per dettagli -->
      <button class="btn btn-sm btn-outline-secondary mb-2 d-none" type="button" data-bs-toggle="collapse"
        data-bs-target="#stepsDebug" aria-expanded="false" aria-controls="stepsDebug">
        Mostra dettagli operazioni
      </button>

      <div class="collapse" id="stepsDebug">
        <textarea id="debug" class="form-control small-text" style="height: 100px;" placeholder="Step intermedi..."
          readonly></textarea>
      </div>
    </div>

    <!-- Prompt e microfono -->
    <div class="section-bottom">
      <div class="prompt-wrapper">
        <textarea id="prompt" class="form-control h-100" placeholder="Prompt..." readonly></textarea>
      </div>
      <div class="partecipant-wrapper col-12">
        <label for="partecipant">Partecipante: (Medico/Paziente)</label><br>
        <select name="partecipant" id="partecipant">
          <option value="">Nessuno</option>
          <option value="medico">Medico</option>
          <option value="paziente">Paziente</option>
        </select>
      </div>
      <div class="mic-wrapper col-12">
        <button id="startBtn" class="btn btn-primary" disabled>
          <i class="bi bi-mic" id="micIcon"></i>
        </button>
      </div>
    </div>
  </div>

  <audio id="audio" style="display: none;"></audio>

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.5/dist/js/bootstrap.bundle.min.js"></script>
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
  <script src="static/js/index.js"></script>
</body>

</html>