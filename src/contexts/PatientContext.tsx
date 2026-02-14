import React, { createContext, useContext, useState, useCallback, useRef, useEffect } from "react";

export type RiskLevel = "Low" | "Medium" | "High";
export type Department = "Cardiology" | "Neurology" | "General Medicine" | "Emergency" | "Gynecology";

export interface Patient {
  id: string;
  age: number;
  gender: string;
  symptoms: string;
  bloodPressure: string;
  heartRate: number;
  temperature: number;
  preExistingConditions: string;
  arrivalTime: string;
  riskScore: number;
  riskLevel: RiskLevel;
  department: Department;
  contributingFactors: string[];
  reasonSummary: string;
  confidenceScore: number;
  synthetic: boolean;
}

interface PatientContextType {
  patients: Patient[];
  selectedPatient: Patient | null;
  addPatient: (p: Patient) => void;
  selectPatient: (p: Patient) => void;
}

const PatientContext = createContext<PatientContextType | undefined>(undefined);

const DEPARTMENTS: Department[] = ["Cardiology", "Neurology", "General Medicine", "Emergency", "Gynecology"];
const SYMPTOMS_POOL = [
  "Chest pain", "Headache", "Fever", "Shortness of breath", "Dizziness",
  "Nausea", "Abdominal pain", "Fatigue", "Cough", "Back pain",
  "Palpitations", "Blurred vision", "Joint pain", "Numbness", "Swelling",
];
const CONDITIONS_POOL = ["Diabetes", "Hypertension", "Asthma", "None", "Heart Disease", "Obesity", "COPD"];
const FACTORS_POOL = [
  "Elevated heart rate", "High blood pressure", "Advanced age", "Multiple symptoms",
  "Pre-existing conditions", "High temperature", "Low oxygen saturation indicator",
];

function rand(min: number, max: number) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function pickRandom<T>(arr: T[], count = 1): T[] {
  const shuffled = [...arr].sort(() => 0.5 - Math.random());
  return shuffled.slice(0, count);
}

function getRiskLevel(score: number): RiskLevel {
  if (score >= 70) return "High";
  if (score >= 40) return "Medium";
  return "Low";
}

export function generateSyntheticPatient(index: number): Patient {
  const riskScore = rand(10, 95);
  const symptoms = pickRandom(SYMPTOMS_POOL, rand(1, 4)).join(", ");
  const department = DEPARTMENTS[rand(0, 4)];
  return {
    id: `SYN-${String(index).padStart(4, "0")}`,
    age: rand(18, 90),
    gender: Math.random() > 0.5 ? "Male" : "Female",
    symptoms,
    bloodPressure: `${rand(90, 180)}/${rand(60, 110)}`,
    heartRate: rand(55, 140),
    temperature: +(rand(360, 404) / 10).toFixed(1),
    preExistingConditions: pickRandom(CONDITIONS_POOL, rand(0, 2)).join(", ") || "None",
    arrivalTime: new Date().toLocaleTimeString(),
    riskScore,
    riskLevel: getRiskLevel(riskScore),
    department,
    contributingFactors: pickRandom(FACTORS_POOL, rand(2, 4)),
    reasonSummary: `Patient presents with ${symptoms.toLowerCase()} suggesting ${department.toLowerCase()} evaluation.`,
    confidenceScore: rand(65, 98),
    synthetic: true,
  };
}

export const PatientProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const counterRef = useRef(1);
  const [patients, setPatients] = useState<Patient[]>(() => {
    const initial: Patient[] = [];
    for (let i = 0; i < 5; i++) {
      initial.push(generateSyntheticPatient(counterRef.current++));
    }
    return initial;
  });
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);

  useEffect(() => {
    const interval = setInterval(() => {
      setPatients(prev => [...prev, generateSyntheticPatient(counterRef.current++)]);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const addPatient = useCallback((p: Patient) => {
    setPatients(prev => [...prev, p]);
  }, []);

  const selectPatient = useCallback((p: Patient) => {
    setSelectedPatient(p);
  }, []);

  return (
    <PatientContext.Provider value={{ patients, selectedPatient, addPatient, selectPatient }}>
      {children}
    </PatientContext.Provider>
  );
};

export function usePatients() {
  const ctx = useContext(PatientContext);
  if (!ctx) throw new Error("usePatients must be used within PatientProvider");
  return ctx;
}
