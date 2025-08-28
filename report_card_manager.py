#!/usr/bin/env python3
"""
report_card_manager.py
Console-based student report card manager.
Requires Python 3.8+. (Recommended: 3.11 or 3.12)
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
import atexit

DATA_FILE = Path("grades.json")


class Student:
    _id_counter = 1

    def __init__(self, name: str):
        self.id: int = Student._id_counter
        Student._id_counter += 1
        self.name: str = name
        self.subjects: Dict[str, float] = {}

    def add_subject(self, subject: str, score: float) -> bool:
        if 0 <= score <= 100:
            self.subjects[subject] = score
            return True
        return False

    def calculate_average(self) -> float:
        if not self.subjects:
            return 0.0
        return sum(self.subjects.values()) / len(self.subjects)

    def get_grade(self) -> str:
        avg = self.calculate_average()
        if avg >= 90:
            return "A"
        if avg >= 75:
            return "B"
        if avg >= 50:
            return "C"
        return "Fail"

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "subjects": self.subjects}

    @classmethod
    def from_dict(cls, data: dict) -> "Student":
        # create without calling __init__ to avoid changing _id_counter inadvertently
        obj = cls.__new__(cls)
        obj.id = int(data["id"])
        obj.name = data["name"]
        obj.subjects = data.get("subjects", {})
        Student._id_counter = max(Student._id_counter, obj.id + 1)
        return obj


class GradeManager:
    def __init__(self, filename: Path = DATA_FILE):
        self.filename: Path = Path(filename)
        self.students: List[Student] = []
        self.load_from_file()

    def add_student(self, name: str) -> int:
        s = Student(name)
        self.students.append(s)
        print(f"✅ Added '{s.name}' with ID {s.id}")
        return s.id

    def find_student(self, student_id: int) -> Optional[Student]:
        for s in self.students:
            if s.id == student_id:
                return s
        return None

    def update_scores(self, student_id: int, subject: str, score: float) -> bool:
        s = self.find_student(student_id)
        if not s:
            print("❌ Student not found.")
            return False
        if not s.add_subject(subject, score):
            print("❌ Score must be between 0 and 100.")
            return False
        print(f"✅ {s.name} - {subject}: {score}")
        return True

    def view_report(self, student_id: int) -> None:
        s = self.find_student(student_id)
        if not s:
            print("❌ Student not found.")
            return
        print("\n--- Report Card ---")
        print(f"ID: {s.id}\nName: {s.name}")
        if s.subjects:
            for sub, score in s.subjects.items():
                print(f"  {sub}: {score}")
        else:
            print("  (no subjects entered)")
        avg = s.calculate_average()
        print(f"Average: {avg:.2f}")
        print(f"Grade: {s.get_grade()}")
        print("--------------------\n")

    def list_students(self) -> None:
        if not self.students:
            print("No students yet.")
            return
        print("\nID  | Name                 | Avg   | Grade")
        print("-------------------------------------------")
        for s in self.students:
            avg = s.calculate_average()
            print(f"{s.id:<4}| {s.name:<20} | {avg:5.2f} | {s.get_grade()}")
        print()

    def delete_student(self, student_id: int) -> bool:
        s = self.find_student(student_id)
        if not s:
            print("❌ Student not found.")
            return False
        self.students.remove(s)
        print(f"🗑️ Deleted {s.name} (ID {s.id})")
        return True

    def save_to_file(self) -> None:
        try:
            data = [s.to_dict() for s in self.students]
            self.filename.parent.mkdir(parents=True, exist_ok=True)
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"💾 Data saved to {self.filename.resolve()}")
        except Exception as e:
            print("❌ Failed to save:", e)

    def load_from_file(self) -> None:
        if not self.filename.exists():
            # no file yet
            return
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.students = [Student.from_dict(d) for d in data]
            print(f"📂 Loaded {len(self.students)} students from {self.filename.resolve()}")
        except Exception as e:
            print("⚠️ Failed to load data:", e)


def input_int(prompt: str) -> Optional[int]:
    try:
        return int(input(prompt).strip())
    except (ValueError, EOFError):
        return None


def input_score(prompt: str) -> Optional[float]:
    try:
        v = input(prompt).strip()
        if not v:
            return None
        return float(v)
    except (ValueError, EOFError):
        return None


def main():
    gm = GradeManager()
    atexit.register(gm.save_to_file)  # ensure saving on normal exit

    menu = """
--- Student Report Card Manager ---
1) Add Student
2) Update Scores (by ID)
3) View Report (by ID)
4) Delete Student
5) List all students
6) Save now
7) Exit
"""
    try:
        while True:
            print(menu)
            choice = input("Choose an option: ").strip()
            if choice == "1":
                name = input("Student name: ").strip()
                if not name:
                    print("❌ Name cannot be empty.")
                    continue
                sid = gm.add_student(name)
                # add subjects
                while True:
                    sub = input("Enter subject (or 'done'): ").strip()
                    if sub.lower() in ("done", "d", ""):
                        break
                    score = input_score(f"Marks for {sub} (0-100): ")
                    if score is None:
                        print("❌ Invalid score.")
                        continue
                    gm.update_scores(sid, sub, score)

            elif choice == "2":
                sid = input_int("Enter student ID: ")
                if sid is None:
                    print("❌ Invalid ID.")
                    continue
                sub = input("Subject name: ").strip()
                if not sub:
                    print("❌ Subject cannot be empty.")
                    continue
                score = input_score("Enter score (0-100): ")
                if score is None:
                    print("❌ Invalid score.")
                    continue
                gm.update_scores(sid, sub, score)

            elif choice == "3":
                sid = input_int("Enter student ID: ")
                if sid is None:
                    print("❌ Invalid ID.")
                    continue
                gm.view_report(sid)

            elif choice == "4":
                sid = input_int("Enter student ID to delete: ")
                if sid is None:
                    print("❌ Invalid ID.")
                    continue
                gm.delete_student(sid)

            elif choice == "5":
                gm.list_students()

            elif choice == "6":
                gm.save_to_file()

            elif choice == "7":
                print("Saving and exiting...")
                gm.save_to_file()
                break

            else:
                print("❌ Invalid choice. Enter 1-7.")

    except (KeyboardInterrupt, EOFError):
        print("\nInterrupted. Saving before exit...")
        gm.save_to_file()


if __name__ == "__main__":
    main()
