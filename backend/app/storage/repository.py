# app/storage/repository.py

from typing import List, Dict


class InMemoryRepository:
    def __init__(self):
        self.patients: List[Dict] = []

    def add_patient(self, patient: Dict):
        self.patients.append(patient)

    def get_all_patients(self) -> List[Dict]:
        return self.patients


repository = InMemoryRepository()
