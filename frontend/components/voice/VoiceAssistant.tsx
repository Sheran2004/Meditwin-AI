"use client";

import { useRouter } from "next/navigation";
import { useRef, useState } from "react";
import { Button } from "@/components/ui/Button";
import { listPatients, sendVoiceCommand } from "@/lib/api";

// Minimal typing for the Web Speech API (not in default TS lib.dom yet).
type SpeechRecognitionResultLike = { transcript: string };
interface SpeechRecognitionLike extends EventTarget {
  lang: string;
  interimResults: boolean;
  start: () => void;
  stop: () => void;
  onresult: ((event: { results: { 0: { 0: SpeechRecognitionResultLike } } }) => void) | null;
  onerror: (() => void) | null;
  onend: (() => void) | null;
}

export function VoiceAssistant() {
  const router = useRouter();
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [response, setResponse] = useState<string | null>(null);
  const [supported, setSupported] = useState(true);
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);

  function startListening() {
    const SpeechRecognitionCtor =
      (window as any).SpeechRecognition ?? (window as any).webkitSpeechRecognition;
    if (!SpeechRecognitionCtor) {
      setSupported(false);
      return;
    }

    const recognition: SpeechRecognitionLike = new SpeechRecognitionCtor();
    recognition.lang = "en-IN";
    recognition.interimResults = false;
    recognition.onresult = async (event) => {
      const heard = event.results[0][0].transcript;
      setTranscript(heard);
      setIsListening(false);

      try {
        const patients = await listPatients();
        const names = patients.map((p) => p.full_name);
        const result = await sendVoiceCommand(heard, names);
        setResponse(result.confirmation_text);

        if (result.intent === "show_patient" && result.patient_name) {
          const match = patients.find((p) => p.full_name.toLowerCase() === result.patient_name!.toLowerCase());
          if (match) router.push(`/doctor/patients/${match.id}`);
        } else if (result.intent === "show_critical_patients") {
          router.push("/doctor/patients");
        }
      } catch (err: any) {
        setResponse(err?.response?.data?.detail ?? "Voice command failed. Is GROQ_API_KEY set in backend/.env?");
      }
    };
    recognition.onerror = () => setIsListening(false);
    recognition.onend = () => setIsListening(false);

    recognitionRef.current = recognition;
    setResponse(null);
    setIsListening(true);
    recognition.start();
  }

  function stopListening() {
    recognitionRef.current?.stop();
    setIsListening(false);
  }

  if (!supported) {
    return <p className="text-xs text-gray-400">Voice commands need Chrome or Edge (Web Speech API not available here).</p>;
  }

  return (
    <div className="flex flex-col gap-2">
      <Button variant={isListening ? "ghost" : "primary"} onClick={isListening ? stopListening : startListening}>
        {isListening ? "Listening… (tap to stop)" : "🎤 Voice command"}
      </Button>
      {transcript && <p className="text-xs text-gray-500 dark:text-gray-400">Heard: &quot;{transcript}&quot;</p>}
      {response && <p className="text-sm text-brand-600 dark:text-brand-100">{response}</p>}
      <p className="text-xs text-gray-400">Try: &quot;Show patient Priya&quot;, &quot;Show critical patients&quot;, &quot;Generate summary&quot;</p>
    </div>
  );
}
