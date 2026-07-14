function base64ToBlob(base64, mimeType) {
  const byteCharacters = atob(base64);
  const byteArrays = [];

  for (let i = 0; i < byteCharacters.length; i += 512) {
    const slice = byteCharacters.slice(i, i + 512);
    const byteNumbers = new Array(slice.length);
    for (let j = 0; j < slice.length; j++) {
      byteNumbers[j] = slice.charCodeAt(j);
    }
    const byteArray = new Uint8Array(byteNumbers);
    byteArrays.push(byteArray);
  }

  return new Blob(byteArrays, { type: mimeType });
}

$(document).ready(function () {
  const startBtn = $('#startBtn');
  const micIcon = $('#micIcon');
  const promptTA = $('#prompt');
  const resultTA = $('#result');
  const debugTA = $('#debug');

  const partecipantSL = $('#partecipant')

  let mediaRecorder;
  let audioChunks = [];
  let isRecording = false;

  
  let partecipant = '';

  partecipantSL.on('change', function () {
    const selected = $(this).val();
    if (!selected) {
      return;
    }
    startBtn.prop('disabled', false);
    partecipant = selected;
  });

  startBtn.on('click', async function () {
    if (!isRecording) {
      debugTA.append("Registrazione iniziata...")
      // Avvia registrazione
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = function (event) {
          audioChunks.push(event.data);
        };

        mediaRecorder.onstop = function () {
          const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
          const formData = new FormData();
          formData.append('audio', audioBlob, 'registrazione.webm');
          console.log("Richiesta a /get_prompt\nPayload: " + JSON.stringify(formData))
          // Prendi il valore della select di id partecipant
          const utente = partecipant || 'medico';
          formData.append('utente', utente);
          $.ajax({
            // url: '/get_prompt',
            url: '/esegui_processo',
            method: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            beforeSend: function () {
              debugTA.append('Invio audio in corso...\n');
              console.log("Invio audio in corso...")
              resultTA.val()
            },
            success: function (data) {
              let messaggio = data.messaggio;
              let risultato = data.risultato;
              console.log(data);
              // resultTA.val(risultato);
              resultTA.data('audioblob',risultato)
              resultTA.val(messaggio).trigger('change');
              debugTA.append(messaggio + '\n');
              // console.log("ho ricevuto: " + JSON.stringify(data) + "\nRichiesta a /to_json\nPayload: " + JSON.stringify(risultato))
              // $.ajax({
              //   url: '/to_json',
              //   method: 'POST',
              //   data: { 'promptText': risultato },
              //   beforeSend: function () {
              //     debugTA.append('Conversione in JSON in corso...\n');
              //     console.log('Conversione in JSON in corso')
              //     resultTA.val()
              //   },
              //   success: function (data) {
              //     let messaggio = data.messaggio;
              // let risultato = data.risultato;
              // console.log(risultato);
              //     debugTA.append(messaggio + '\n');
              //     $.ajax({
              //       url: '/parse_output',
              //       method: 'POST',
              //       contentType: 'application/json',
              //       dataType: 'json',
              //       beforeSend: function () {
              //         const intent = data.risultato.intent;
              //         let debugMsg = '';
              //         let ok = true
              //         if (intent === 'crea_dt') {
              //           debugMsg = 'Creazione del Digital Twin in corso...';
              //         } else if (intent === 'simula_dt') {
              //           debugMsg = 'Simulazione del Digital Twin in corso...';
              //         } else if (intent === 'analizza') {
              //           debugMsg = 'Analisi della simulazione in corso...';
              //         } else if (intent === 'confronta') {
              //           debugMsg = 'Confronto tra le terapie in corso...';
              //         }
              //         else {
              //           debugMsg = 'Intent non riconosciuto'
              //           ok = false
              //         }
              //         resultTA.val(debugMsg);
              //         debugTA.append(debugMsg + '\n');
              //         console.log(debugMsg)
              //         if (!ok)
              //           return
              //       },
              //       data: { 'intentJson': risultato},
              //       success: function (data) {
              //         let messaggio = data.messaggio;
              //         let risultato = data.risultato;
              //         console.log(risultato);
              //         debugTA.append(messaggio + '\n');
              //         resultTA.val(risultato).
              // resultTA.val(messaggio);trigger('change');
              //       },
              //       // error: function () {
              //       //   console.error("Errore durante l'operazione")
              //       //   debugTA.append("Errore durante l'operazione")
              //       //   resultTA.val()
              //       // }
              //     });
              //   },
              //   // error: function () {
              //   //   console.error("Errore durante conversione in JSON")
              //   //   debugTA.append("Errore durante conversione in JSON")
              //   // }
              // });
            },
            // error: function () {
            //   console.log("Errore nell'invio dell'audio")
            //   debugTA.append("Errore nell'invio dell'audio")
            //   resultTA.val()
            // }
          });
        };

        mediaRecorder.start();
        isRecording = true;
        micIcon.removeClass('bi-mic').addClass('bi-mic-mute');
        debugTA.append('Registrazione avviata...\n');
      } catch (err) {
        alert('Errore microfono: ' + err.message);
      }

    } else {
      // Ferma registrazione
      if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        debugTA.append('Registrazione fermata.\n');
      }

      isRecording = false;
      micIcon.removeClass('bi-mic-mute').addClass('bi-mic');
    }
  });

  resultTA.on('change', function () {
  const base64Audio = $(this).data('audioblob');

  if (!base64Audio || typeof base64Audio !== 'string') {
    console.warn("Nessun audio base64 valido trovato.");
    return;
  }

  const audioBlob = base64ToBlob(base64Audio, 'audio/mpeg');
  const audioUrl = URL.createObjectURL(audioBlob);

  const audio = document.getElementById('audio');
  audio.src = audioUrl;
  audio.play();

  audio.onended = function () {
    URL.revokeObjectURL(audioUrl);
    startBtn.prop('disabled', false);
  };
});

  // resultTA.on('change', function () {
  //   const text = $(this).val();
  //   console.log('testo: ' + text);
  //   $.ajax({
  //     url: '/to_speech',
  //     method: 'POST',
  //     data: { "text": text },
  //     xhrFields: { responseType: 'blob' },
  //     success: function (blob) {
  //       const audioUrl = URL.createObjectURL(blob);
  //       const audio = document.getElementById('audio');
  //       audio.src = audioUrl;
  //       audio.play();

  //       audio.onended = function () {
  //         URL.revokeObjectURL(audioUrl);
  //         startBtn.prop('disabled', false);
  //       };
  //     },
  //     // error: function (xhr, status, error) {
  //     //   console.error('Errore nella richiesta /to_speech:', error);

  //     // }
  //   });
  // });
});
