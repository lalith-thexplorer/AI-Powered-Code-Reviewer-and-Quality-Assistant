"""Module for managing a simple student record system."""


class Student:

    def __init__(self, name, age, grade):
        self.name = name
        self.age = age
        self.grade = grade

    def get_name(self):
        """Return the student's name."""
        return self.name

    def get_age(self):
        return self.age

    def get_grade(self):
        return self.grade

    def promote(self):
        """Promote the student to the next grade level."""
        self.grade += 1

    def summary(self):
        return f"{self.name}, Age: {self.age}, Grade: {self.grade}"


class Classroom:

    def __init__(self, room_number):
        self.room_number = room_number
        self.students = []

    def add_student(self, student):
        """Add a Student instance to the classroom roster."""
        self.students.append(student)

    def remove_student(self, name):
        self.students = [s for s in self.students if s.get_name() != name]

    def get_student_count(self):
        """Return total number of students currently enrolled."""
        return len(self.students)

    def list_students(self):
        return [s.get_name() for s in self.students]
