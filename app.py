import streamlit as st
import openai

st.set_page_config(page_title="Certificazione Team Work – Modulo Singolo", layout="centered")

# --- Setup Iniziale ---
if "step" not in st.session_state:
    st.session_state.step = "profilo"
    st.session_state.profilo_utente = {}
    st.session_state.domande = []
    st.session_state.indice = 0
    st.session_state.risposte = []
    st.session_state.punteggi = []
    st.session_state.valutazioni = []

soft_skills = [
    "Comunicazione",
    "Ascolto attivo",
    "Rispettare le opinioni altrui",
    "Gestione dei conflitti",
    "Collaborazione proattiva",
    "Creatività",
    "Responsabilità",
    "Fiducia",
    "Compromesso",
    "Leadership"
]

# --- Funzioni ---
def genera_domanda_softskill(nome, skill, storia_risposte):
    contesto = "\n".join([f"D: {d}\nR: {r}" for d, r in storia_risposte]) if storia_risposte else ""
    prompt = f"""
Agisci come un team composto da:
- uno psicologo del lavoro (Paul E. Spector),
- uno specialista di intelligenza emotiva (Daniel Goleman),
- un esperto di comunicazione empatica (Marshall Rosenberg),
- un esperto di comportamenti organizzativi (Chris Argyris),
- un teorico delle competenze (David McClelland).

Genera una singola domanda comportamentale per valutare la soft skill "{skill}" come sotto-componente del Team Work.

La domanda deve essere chiara, professionale e suddivisa in tre parti:
1. Scenario (reale e lavorativo)
2. Problema (specifico e concreto)
3. Domanda (cosa faresti?)

Evita ambiguità, usa linguaggio semplice e chiaro. Ogni parte su una riga diversa.
{contesto}
"""
    out = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return out.choices[0].message.content.strip()

def valuta_risposta(risposta, skill):
    if not risposta.strip():
        return f"{skill}: 0\nMotivazione: Nessuna risposta fornita."
    prompt = f"""Valuta la seguente risposta rispetto alla sotto-soft skill: {skill}.
Risposta: \"{risposta}\"
Assegna un punteggio da 0 a 100 e spiega brevemente.
Formato:
{skill}: XX
Motivazione: ..."""
    out = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return out.choices[0].message.content.strip()

def genera_descrizione(parziale):
    prompt = f"""
Agisci come un team di:
- psicologi del lavoro (Paul E. Spector),
- specialisti di intelligenza emotiva (Daniel Goleman),
- esperti di comunicazione empatica (Marshall Rosenberg),
- esperti di comportamenti organizzativi (Chris Argyris),
- teorici delle competenze (David McClelland).

Il candidato {parziale['nome']} ha ottenuto una media di {parziale['media']}/100 nella sotto-soft skill {parziale['skill']}.

Analizza le seguenti risposte e motivazioni:
{parziale['risposte']}

Genera un report suddiviso in 4 sezioni:
1. Sintesi punteggio e livello
2. Analisi dettagliata dei comportamenti osservati (con riferimenti alle risposte)
3. Suggerimenti pratici per migliorare
4. Corso formativo consigliato (solo il titolo)

Tono professionale, coerente con il livello. Se il punteggio è basso, sii severo ma costruttivo.
"""
    out = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return out.choices[0].message.content.strip()

# --- Pagina Profilo ---
if st.session_state.step == "profilo":
    st.title("Certificazione Team Work – Modulo Singolo")
    st.subheader("Compila il profilo iniziale")

    nome = st.text_input("Nome e cognome")
    eta = st.number_input("Età", 16, 99, 30)
    titolo = st.text_input("Titolo di studio")
    azienda = st.text_input("Azienda attuale o precedente")
    ruolo = st.text_input("Ruolo")
    anni_settore = st.slider("Anni nel settore", 0, 40, 5)
    anni_ruolo = st.slider("Anni nel ruolo", 0, 40, 3)
    skill_scelta = st.selectbox("Sotto-soft skill da certificare", soft_skills)

    if st.button("Inizia il modulo"):
        if all([nome, eta, titolo, azienda, ruolo, skill_scelta]):
            st.session_state.profilo_utente = {
                "nome": nome, "eta": eta, "titolo": titolo,
                "azienda": azienda, "ruolo": ruolo,
                "anni_settore": anni_settore, "anni_ruolo": anni_ruolo,
                "skill": skill_scelta
            }
            domanda = genera_domanda_softskill(nome, skill_scelta, [])
            st.session_state.domande = [domanda]
            st.session_state.step = "test"
            st.rerun()
        else:
            st.error("Completa tutti i campi per iniziare")

# --- Pagina Test ---
elif st.session_state.step == "test":
    st.title("Test – " + st.session_state.profilo_utente['skill'])
    i = st.session_state.indice
    st.markdown(f"**Domanda {i+1} di 20**")
    for line in st.session_state.domande[i].splitlines():
        st.markdown(line)

    risposta = st.text_area("La tua risposta", key=f"risposta_{i}")

    if st.button("Invia risposta"):
        st.session_state.risposte.append(risposta)
        valutazione = valuta_risposta(risposta, st.session_state.profilo_utente['skill'])
        st.session_state.valutazioni.append(valutazione)
        punteggio = 0
        for line in valutazione.splitlines():
            if line.startswith(st.session_state.profilo_utente['skill']):
                punteggio = int("".join(filter(str.isdigit, line)))
        st.session_state.punteggi.append(punteggio)

        st.session_state.indice += 1
        if st.session_state.indice < 20:
            nuova = genera_domanda_softskill(st.session_state.profilo_utente['nome'], st.session_state.profilo_utente['skill'], list(zip(st.session_state.domande, st.session_state.risposte)))
            st.session_state.domande.append(nuova)
        else:
            st.session_state.step = "risultato"
        st.rerun()

# --- Pagina Risultato ---
elif st.session_state.step == "risultato":
    st.title("✅ Modulo completato")
    media = round(sum(st.session_state.punteggi)/len(st.session_state.punteggi), 2)
    st.markdown(f"### Media punteggio: **{media}/100**")

    if media >= 70:
        st.success("Hai ottenuto il badge!")
        st.image("https://raw.githubusercontent.com/CertSkill/teamwork-cert/main/badge.png", width=250)
    else:
        st.warning("Continua ad allenarti per ottenere la certificazione.")

    st.markdown("### 📄 Analisi del profilo")
    report_input = {
        "nome": st.session_state.profilo_utente['nome'],
        "skill": st.session_state.profilo_utente['skill'],
        "media": media,
        "risposte": "\n\n".join(st.session_state.valutazioni)
    }
    descrizione = genera_descrizione(report_input)
    for r in descrizione.split("\n"):
        st.markdown(r)

    if st.button("🔁 Torna all’inizio"):
        st.session_state.clear()
        st.rerun()
