import csv
import os
from django.core.management.base import BaseCommand
from core.models import Quiz, Question

class Command(BaseCommand):
    help = 'Import quiz questions from a CSV file'

    def handle(self, *args, **kwargs):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Path to the CSV file (in the same directory as the script)
        file_path = os.path.join(script_dir, 'quiz_questions.csv')

        # Log the file path for debugging
        self.stdout.write(f"Looking for CSV file at: {file_path}")

        # Create or get the quiz
        quiz, created = Quiz.objects.get_or_create(title="Environmental Quiz")

        # Open the CSV file
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            # Loop through each row in the CSV
            for row in reader:
                question_text = row['Question']
                option_a = row['Option A']
                option_b = row['Option B']
                option_c = row['Option C']
                option_d = row['Option D']
                correct_answer = row['Correct Answer']

                # Create a new Question object
                question = Question.objects.create(
                    quiz=quiz,
                    question_text=question_text,
                    option1=option_a,
                    option2=option_b,
                    option3=option_c,
                    option4=option_d,
                    correct_option=correct_answer
                )

                # Log success
                self.stdout.write(self.style.SUCCESS(f'Successfully imported question: "{question_text}"'))