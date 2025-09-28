"""
Python Learning Journey - Day Seven
Week One Comprehensive Review & Progress Assessment
Date: September 28, 2025
Author: Cosmas Onyekwelu
"""

import json
from datetime import datetime, timedelta


class WeekOneReview:
    def __init__(self):
        self.start_date = datetime(2024, 9, 22)
        self.end_date = datetime(2024, 9, 28)
        self.days_completed = 6
        self.projects_built = 3

        self.learning_timeline = {
            "Day 1": {
                "date": "Sep 22, 2024",
                "focus": "Python Fundamentals & Setup",
                "topics": ["Variables", "Data Types", "Basic Syntax", "GitHub Setup"],
                "achievements": ["First Python Program", "Environment Configuration"]
            },
            "Day 2": {
                "date": "Sep 23, 2024",
                "focus": "Backend Introduction & Linux",
                "topics": ["Server Setup", "Web Servers", "Database Concepts"],
                "achievements": ["Backend Orientation", "Server Understanding"]
            },
            "Day 3": {
                "date": "Sep 24, 2024",
                "focus": "Flask & Web Development",
                "topics": ["REST APIs", "HTTP Methods", "JSON Handling"],
                "achievements": ["First Web Application", "API Development"]
            },
            "Day 4": {
                "date": "Sep 25, 2024",
                "focus": "Control Flow & Algorithms",
                "topics": ["Conditionals", "Loops", "Problem Solving"],
                "achievements": ["Number Guessing Game", "Algorithm Practice"]
            },
            "Day 5": {
                "date": "Sep 26, 2024",
                "focus": "Data Structures Mastery",
                "topics": ["Lists", "Dictionaries", "Sets", "Tuples"],
                "achievements": ["Gradebook System", "Data Structure Applications"]
            },
            "Day 6": {
                "date": "Sep 27, 2024",
                "focus": "Algorithms & File Handling",
                "topics": ["Sorting", "Searching", "File I/O", "CSV Processing"],
                "achievements": ["Contact Book", "File Persistence"]
            }
        }

    def display_week_summary(self):
        """Display comprehensive week 1 summary"""
        print("=" * 70)
        print(" WEEK 1: PYTHON LEARNING JOURNEY SUMMARY")
        print("=" * 70)
        print(
            f" Period: {self.start_date.strftime('%b %d')} - {self.end_date.strftime('%b %d, %Y')}")
        print(f" Days Completed: {self.days_completed}")
        print(f" Projects Built: {self.projects_built}")
        print(f" Current Level: Beginner → Intermediate")

        self.display_progress_chart()
        self.display_daily_breakdown()
        self.display_skills_assessment()
        self.display_projects_showcase()

    def display_progress_chart(self):
        """Display visual progress chart"""
        print("\n PROGRESS CHART")
        print("-" * 50)

        skills = {
            "Basic Syntax": 95,
            "Variables & Types": 90,
            "Control Flow": 85,
            "Functions": 80,
            "Data Structures": 75,
            "File Handling": 70,
            "Algorithms": 65,
            "Web Development": 70
        }

        for skill, percentage in skills.items():
            bars = "█" * (percentage // 5)
            spaces = " " * (20 - len(bars))
            print(f"{skill:<18} [{bars}{spaces}] {percentage}%")

    def display_daily_breakdown(self):
        """Display detailed daily progress"""
        print("\n DAILY BREAKDOWN")
        print("-" * 50)

        for day, info in self.learning_timeline.items():
            print(f"\n{day} ({info['date']}):")
            print(f"  Focus: {info['focus']}")
            print(f"  Topics: {', '.join(info['topics'])}")
            print(f"  Achievements: {', '.join(info['achievements'])}")

    def display_skills_assessment(self):
        """Display skills self-assessment"""
        print("\n SKILLS ASSESSMENT")
        print("-" * 50)

        assessment = {
            "Expert (90-100%)": ["Basic Syntax", "Variables"],
            "Advanced (80-89%)": ["Control Flow", "Data Structures"],
            "Intermediate (70-79%)": ["Functions", "File Handling", "Web Dev"],
            "Beginner+ (60-69%)": ["Algorithms"],
            "Next Focus": ["OOP", "Databases", "Testing"]
        }

        for level, skills in assessment.items():
            print(f"{level}:")
            for skill in skills:
                print(f"  • {skill}")

    def display_projects_showcase(self):
        """Display projects completed"""
        print("\n🏆 PROJECTS SHOWCASE")
        print("-" * 50)

        projects = {
            "Number Guessing Game": {
                "day": "Day 4",
                "skills": ["Control Flow", "User Input", "Random Numbers"],
                "complexity": "Beginner"
            },
            "Student Gradebook System": {
                "day": "Day 5",
                "skills": ["Data Structures", "Dictionaries", "Calculations"],
                "complexity": "Intermediate"
            },
            "Contact Book Manager": {
                "day": "Day 6",
                "skills": ["File I/O", "CSV Processing", "Search Algorithms"],
                "complexity": "Intermediate+"
            }
        }

        for project, info in projects.items():
            print(f"\n {project} ({info['day']})")
            print(f"   Skills: {', '.join(info['skills'])}")
            print(f"   Level: {info['complexity']}")

    def generate_week_report(self):
        """Generate a comprehensive week report"""
        report = {
            "summary": {
                "total_days": self.days_completed,
                "projects_completed": self.projects_built,
                "start_date": self.start_date.isoformat(),
                "end_date": self.end_date.isoformat(),
                "overall_progress": "Excellent"
            },
            "technical_skills": {
                "mastered": ["Python Syntax", "Variables", "Basic Operations", "Git Usage"],
                "proficient": ["Control Flow", "Data Structures", "Basic Algorithms"],
                "developing": ["File Handling", "Web Development", "Advanced Algorithms"],
                "next_focus": ["OOP", "Database Integration", "Web Frameworks"]
            },
            "achievements": [
                "Consistent daily coding practice",
                "Multiple working projects built",
                "GitHub repository maintained",
                "Progressive skill development"
            ],
            "week_2_recommendations": [
                "Start Object-Oriented Programming",
                "Practice with real databases",
                "Build a full-stack application",
                "Learn about testing and debugging"
            ]
        }

        return report


def demonstrate_week_progress():
    """Demonstrate skills gained through code examples"""
    print("\n" + "=" * 70)
    print(" CODE PROGRESS DEMONSTRATION")
    print("=" * 70)

    # Show evolution from Day 1 to Day 6
    print("\n EVOLUTION OF SKILLS")
    print("-" * 40)

    # Day 1 level code
    print("Day 1 - Basic Syntax:")
    day1_code = """
# Basic variables and operations
name = "Python Learner"
age = 25
print(f"Hello {name}, age {age}")
"""
    print(day1_code)

    # Day 6 level code
    print("Day 6 - Advanced Application:")
    day6_code = """
# File handling and data processing
def analyze_contact_book(filename):
    with open(filename, 'r') as file:
        contacts = csv.DictReader(file)
        return [contact for contact in contacts if contact['active'] == 'yes']
"""
    print(day6_code)

    # Progress statistics
    print("\n WEEK 1 STATISTICS")
    print("-" * 30)
    stats = {
        "Lines of Code Written": "500+",
        "Concepts Learned": "25+",
        "Hours Practiced": "20+",
        "Errors Debugged": "50+",
        "Git Commits": "7+"
    }

    for stat, value in stats.items():
        print(f"{stat}: {value}")


def main():
    """Main execution function"""
    print(" DAY 7: WEEK 1 COMPREHENSIVE REVIEW")
    print("=" * 70)

    # Generate and display week review
    review = WeekOneReview()
    review.display_week_summary()

    # Demonstrate progress
    demonstrate_week_progress()

    # Generate detailed report
    report = review.generate_week_report()

    print("\n DETAILED WEEK REPORT")
    print("-" * 30)
    print(f"Overall Progress: {report['summary']['overall_progress']}")
    print(
        f"Technical Skills Mastered: {len(report['technical_skills']['mastered'])}")
    print(f"Key Achievements: {len(report['achievements'])}")

    print("\n READY FOR WEEK 2!")
    print("=" * 40)
    print("Next week's focus areas:")
    for i, recommendation in enumerate(report['week_2_recommendations'], 1):
        print(f"{i}. {recommendation}")


if __name__ == "__main__":
    main()
