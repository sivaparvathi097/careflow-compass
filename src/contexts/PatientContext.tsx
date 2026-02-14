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

// Ward/Bed types for shared state
export interface Ward {
  name: string;
  totalBeds: number;
  occupied: number;
}

export type DepartmentsData = Record<Department, Ward[]>;
export type AdmissionLogs = Record<string, number[]>; // "Dept:Ward" -> timestamps

// localStorage keys
const STORAGE_KEY_DEPTS = "careflow_departments_data";
const STORAGE_KEY_LOGS = "careflow_admission_logs";

// Initial data (used only if nothing in localStorage)
const INITIAL_DEPARTMENTS: DepartmentsData = {
  Cardiology: [
    { name: "CCU", totalBeds: 12, occupied: 9 },
    { name: "Ward A", totalBeds: 16, occupied: 10 },
    { name: "Ward B", totalBeds: 12, occupied: 8 },
  ],
  Neurology: [
    { name: "Neuro ICU", totalBeds: 8, occupied: 7 },
    { name: "Ward C", totalBeds: 14, occupied: 8 },
  ],
  "General Medicine": [
    { name: "Ward D", totalBeds: 20, occupied: 14 },
    { name: "Ward E", totalBeds: 20, occupied: 16 },
    { name: "Ward F", totalBeds: 20, occupied: 12 },
  ],
  Emergency: [
    { name: "ER Bay", totalBeds: 15, occupied: 13 },
    { name: "Observation", totalBeds: 10, occupied: 7 },
  ],
  Gynecology: [
    { name: "Ward G", totalBeds: 10, occupied: 5 },
    { name: "Ward H", totalBeds: 10, occupied: 7 },
  ],
};

interface PatientContextType {
  patients: Patient[];
  selectedPatient: Patient | null;
  addPatient: (p: Patient) => void;
  selectPatient: (p: Patient) => void;
  // Shared departments/beds state
  departments: DepartmentsData;
  admissionLogs: AdmissionLogs;
  incrementOccupied: (dept: Department, wardName: string) => void;
  decrementOccupied: (dept: Department, wardName: string) => void;
  getDepartmentStats: (dept: Department) => { totalBeds: number; occupied: number; available: number };
  getForecastHours: (dept: Department, wardName: string, ward: Ward) => number | null;
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

  // Load departments from localStorage or use initial data
  const [departments, setDepartments] = useState<DepartmentsData>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY_DEPTS);
      if (saved) return JSON.parse(saved);
    } catch (e) { /* ignore */ }
    return INITIAL_DEPARTMENTS;
  });

  // Load admission logs from localStorage
  const [admissionLogs, setAdmissionLogs] = useState<AdmissionLogs>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY_LOGS);
      if (saved) return JSON.parse(saved);
    } catch (e) { /* ignore */ }
    return {};
  });

  // Persist departments to localStorage
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY_DEPTS, JSON.stringify(departments));
  }, [departments]);

  // Persist admission logs to localStorage
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY_LOGS, JSON.stringify(admissionLogs));
  }, [admissionLogs]);

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

  // Increment occupied bed count and log admission
  const incrementOccupied = useCallback((dept: Department, wardName: string) => {
    // Log admission timestamp
    const key = `${dept}:${wardName}`;
    setAdmissionLogs(prev => ({
      ...prev,
      [key]: [...(prev[key] || []), Date.now()]
    }));

    // Update occupied count
    setDepartments(prev => {
      const updatedWards = prev[dept].map(ward => {
        if (ward.name === wardName && ward.occupied < ward.totalBeds) {
          return { ...ward, occupied: ward.occupied + 1 };
        }
        return ward;
      });
      return { ...prev, [dept]: updatedWards };
    });
  }, []);

  // Decrement occupied bed count
  const decrementOccupied = useCallback((dept: Department, wardName: string) => {
    setDepartments(prev => {
      const updatedWards = prev[dept].map(ward => {
        if (ward.name === wardName && ward.occupied > 0) {
          return { ...ward, occupied: ward.occupied - 1 };
        }
        return ward;
      });
      return { ...prev, [dept]: updatedWards };
    });
  }, []);

  // Get aggregated stats for a department
  const getDepartmentStats = useCallback((dept: Department) => {
    const wards = departments[dept] || [];
    const totalBeds = wards.reduce((sum, w) => sum + w.totalBeds, 0);
    const occupied = wards.reduce((sum, w) => sum + w.occupied, 0);
    return { totalBeds, occupied, available: totalBeds - occupied };
  }, [departments]);

  // Calculate forecast hours for a ward
  const getForecastHours = useCallback((dept: Department, wardName: string, ward: Ward): number | null => {
    const remaining = ward.totalBeds - ward.occupied;
    if (remaining <= 0) return 0;

    const key = `${dept}:${wardName}`;
    const logs = admissionLogs[key] || [];
    const oneHourAgo = Date.now() - 60 * 60 * 1000;
    const recentAdmissions = logs.filter(t => t >= oneHourAgo);
    const rate = recentAdmissions.length;

    if (rate === 0) return null;
    return Math.round((remaining / rate) * 10) / 10;
  }, [admissionLogs]);

  return (
    <PatientContext.Provider value={{
      patients,
      selectedPatient,
      addPatient,
      selectPatient,
      departments,
      admissionLogs,
      incrementOccupied,
      decrementOccupied,
      getDepartmentStats,
      getForecastHours
    }}>
      {children}
    </PatientContext.Provider>
  );
};

export function usePatients() {
  const ctx = useContext(PatientContext);
  if (!ctx) throw new Error("usePatients must be used within PatientProvider");
  return ctx;
}
