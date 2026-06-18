<script>
    import { base } from '$app/paths';
    import { onMount } from 'svelte';

    let currentPage = $state(1); 
    let selectedDay = $state('');
    let selectedTime = $state('');
    let patientName = $state('Patient'); 

    let statusText = $state('Klar til første måling');
    let isMeasuring = $state(false);
    let showResultButtons = $state(false);
    let isSent = $state(false); 

    let measurements = $state([
        { sys: '-', dia: '-', puls: '-' },
        { sys: '-', dia: '-', puls: '-' },
        { sys: '-', dia: '-', puls: '-' }
    ]);

    let average = $state({ sys: '...', dia: '...', puls: '...' });

    onMount(() => {
        const gemtNavn = localStorage.getItem('patientName');
        if (gemtNavn) {
            patientName = gemtNavn.trim().charAt(0).toUpperCase() + gemtNavn.trim().slice(1);
        }
    });

    function selectDay(day) { selectedDay = day; }
    function selectTime(time) { selectedTime = time; }

    async function startPage() {
        currentPage = 2;
        statusText = 'Sid helt roligt.';
        isMeasuring = true;
        showResultButtons = false;
        isSent = false; 

        measurements = [
            { sys: '-', dia: '-', puls: '-' },
            { sys: '-', dia: '-', puls: '-' },
            { sys: '-', dia: '-', puls: '-' }
        ];
        average = { sys: '...', dia: '...', puls: '...' };

        try {
            const response = await fetch(`${base}/api/patient`, { method: 'POST' });
            
            if (!response.ok) {
                statusText = 'Fejl ved opstart af måling.';
                isMeasuring = false;
                showResultButtons = true;
                return;
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';
            let idx = 0;

            statusText = 'Måling i gang... Vent på Arduino.';

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                let lines = buffer.split('\n');
                buffer = lines.pop(); 

                for (let line of lines) {
                    line = line.trim();
                    if (!line) continue;

                    if (line.startsWith('FEJL:')) {
                        statusText = line.replace('FEJL:', '');
                        break;
                    }

                    if (line === 'STATUS:FÆRDIG') {
                        statusText = 'Alle målinger er modtaget!';
                        continue;
                    }

                    const dele = line.split(',');
                    if (dele.length === 3 && idx < 3) {
                        measurements[idx] = {
                            sys: parseInt(dele[0]),
                            dia: parseInt(dele[1]),
                            puls: parseInt(dele[2])
                        };
                        idx++;
                        statusText = `Måling ${idx} registreret.`;
                    }
                }
            }

            const f = measurements.filter(m => m.sys !== '-');
            if (f.length > 0) {
                average = {
                    sys: Math.round(f.reduce((s, m) => s + m.sys, 0) / f.length),
                    dia: Math.round(f.reduce((s, m) => s + m.dia, 0) / f.length),
                    puls: Math.round(f.reduce((s, m) => s + m.puls, 0) / f.length)
                };
            }

        } catch (err) {
            console.error(err);
            statusText = 'Mistede forbindelsen til serveren.';
        } finally {
            isMeasuring = false;
            showResultButtons = true;
        }
    }

    function goBack() {
        currentPage = 1;
        selectedDay = '';
        selectedTime = '';
        isSent = false;
    }

    async function sendToDoctor() {
        statusText = 'Gemmer målinger i databasen...';
        try {
            const response = await fetch(`${base}/api/patient/save measurements`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    patientId: 1, 
                    systolic: average.sys,
                    diastolic: average.dia,
                    pulse: average.puls
                })
            });

            const resData = await response.json();

            if (response.ok) {
                isSent = true;
                statusText = 'Data overført med succes.';
            } else {
                statusText = 'Fejl: Kunne ikke gemme.';
            }
        } catch (err) {
            console.error(err);
            statusText = 'Netværksfejl: Kunne ikke sende til databasen.';
        }
    }
</script>

<div class="min-h-screen w-full flex items-center justify-center bg-[#bfdbfe] p-4">
    <div class="w-90 h-130 bg-black rounded-[45px] border-8 border-[#9c9c9c] shadow-[0_8px_25px_rgba(0,0,0,0.35)] text-white p-6 relative flex flex-col items-center select-none box-border">
        
        {#if currentPage === 1}
            <div class="w-full flex flex-col items-center pt-6 flex-1">
                <h1 class="text-[25px] font-normal mb-8">Velkommen, {patientName}</h1>
                
                <div class="w-full flex justify-around mt-4">
                    <div class="flex flex-col items-center">
                        <h3 class="underline text-[17px] mb-4 text-zinc-300">Vælg dag</h3>
                        <button onclick={() => selectDay('Dag 1')} class="text-[18px] font-bold my-3 transition-colors outline-none {selectedDay === 'Dag 1' ? 'text-white underline' : 'text-zinc-400 hover:text-zinc-200'}">Dag 1</button>
                        <button onclick={() => selectDay('Dag 2')} class="text-[18px] font-bold my-3 transition-colors outline-none {selectedDay === 'Dag 2' ? 'text-white underline' : 'text-zinc-400 hover:text-zinc-200'}">Dag 2</button>
                        <button onclick={() => selectDay('Dag 3')} class="text-[18px] font-bold my-3 transition-colors outline-none {selectedDay === 'Dag 3' ? 'text-white underline' : 'text-zinc-400 hover:text-zinc-200'}">Dag 3</button>
                    </div>
                    <div class="flex flex-col items-center">
                        <h3 class="underline text-[17px] mb-4 text-zinc-300">Vælg tidspunkt</h3>
                        <button onclick={() => selectTime('Morgen')} class="text-[18px] font-bold my-3 transition-colors outline-none {selectedTime === 'Morgen' ? 'text-white underline' : 'text-zinc-400 hover:text-zinc-200'}">Morgen</button>
                        <button onclick={() => selectTime('Aften')} class="text-[18px] font-bold my-3 transition-colors outline-none {selectedTime === 'Aften' ? 'text-white underline' : 'text-zinc-400 hover:text-zinc-200'}">Aften</button>
                    </div>
                </div>
                <div class="w-full flex justify-center mt-auto mb-10 min-h-11">
                    {#if selectedDay && selectedTime}
                        <button onclick={startPage} class="bg-[#009846] text-white font-bold text-[15px] px-6 py-2.5 rounded uppercase tracking-wide shadow-md hover:bg-[#007a38] transition-colors">
                            START MÅLING
                        </button>
                    {/if}
                </div>
            </div>
        {/if}

        {#if currentPage === 2}
            <div class="w-full flex flex-col items-center pt-2 flex-1 relative">
                
                <h2 class="text-[22px] font-medium leading-tight text-center mt-2">{selectedDay}<br>{selectedTime}</h2>
                
                {#if !isSent}
                    <button onclick={goBack} class="bg-zinc-800 text-white text-[12px] px-3 py-1 rounded mt-2 self-center hover:bg-zinc-700 transition-colors" disabled={isMeasuring}>← Tilbage</button>
                {/if}

                <div class="w-full grid grid-cols-5 gap-1.5 mt-8 pr-2 pl-1 text-center text-[13px] items-center">
                    <div class="text-left font-bold text-zinc-300 col-span-5 grid grid-cols-5 gap-1.5 mb-1 text-[11px]">
                        <div>1. måling</div>
                        <div>2. måling</div>
                        <div>3. måling</div>
                        <div>Gns.</div>
                        <div></div> 
                    </div>

                    <div class="font-bold text-sm text-white">{measurements[0].sys}</div>
                    <div class="font-bold text-sm text-white">{measurements[1].sys}</div>
                    <div class="font-bold text-sm text-white">{measurements[2].sys}</div>
                    <div class="font-bold text-sm text-white">{average.sys}</div> 
                    <div class="text-[#0099ff] font-bold text-left pl-1 text-[12px]">SYS</div>

                    <div class="font-bold text-sm text-white">{measurements[0].dia}</div>
                    <div class="font-bold text-sm text-white">{measurements[1].dia}</div>
                    <div class="font-bold text-sm text-white">{measurements[2].dia}</div>
                    <div class="font-bold text-sm text-white">{average.dia}</div> 
                    <div class="text-[#0099ff] font-bold text-left pl-1 text-[12px]">DIA</div>

                    <div class="font-bold text-sm text-white">{measurements[0].puls}</div>
                    <div class="font-bold text-sm text-white">{measurements[1].puls}</div>
                    <div class="font-bold text-sm text-white">{measurements[2].puls}</div>
                    <div class="font-bold text-sm text-white">{average.puls}</div> 
                    <div class="text-[#0099ff] font-bold text-left pl-1 text-[12px]">PULS</div>
                </div>

                <div class="mt-auto mb-4 text-center px-4">
                    {#if isSent}
                        <div class="text-[15px] font-bold text-emerald-400 mb-1">✓ Sendt til læge.</div>
                        <div class="text-[13px] text-zinc-200 leading-normal">Du kan nu slukke blodtryksmåleren.</div>
                    {:else}
                        <div class="text-[13px] text-zinc-300 italic min-h-5">{statusText}</div>
                    {/if}
                </div>

                <div class="w-full flex justify-center gap-3 mb-10 min-h-10">
                    {#if showResultButtons}
                        {#if isSent}
                            <button onclick={goBack} class="bg-zinc-800 text-white font-bold text-[14px] px-6 py-2 rounded shadow hover:bg-zinc-700 transition-colors">
                                Tilbage til start
                            </button>
                        {:else}
                            <button onclick={startPage} class="bg-[#b00000] text-white font-bold text-[14px] px-4 py-2 rounded shadow hover:bg-[#8f0000] transition-colors">
                                Mål igen
                            </button>
                            <button onclick={sendToDoctor} class="bg-[#009846] text-white font-bold text-[14px] px-4 py-2 rounded shadow hover:bg-[#007a38] transition-colors">
                                Send til læge
                            </button>
                        {/if}
                    {/if}
                </div>
            </div>
        {/if}

        <div class="w-11.25 h-11.25 bg-zinc-900 rounded-full absolute bottom-4 left-1/2 -translate-x-1/2 border border-zinc-800"></div>
    </div>
</div>