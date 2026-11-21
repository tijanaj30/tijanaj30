import whisper, json, sys
m = whisper.load_model('medium')
prompt = "Dobili ste nove zube, probate ih, ali vam se nešto tu ne dopada. Zubni tehničar, stomatolog, privremene krune, završni rad."
r = m.transcribe(sys.argv[1], language='sr', word_timestamps=True, initial_prompt=prompt, condition_on_previous_text=False, verbose=False)
json.dump(r, open(sys.argv[2], 'w'), ensure_ascii=False, indent=1)
for s in r['segments']:
    print(f"{s['start']:7.2f} {s['end']:7.2f}  {s['text']}")
