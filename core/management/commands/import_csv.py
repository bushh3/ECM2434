import csv
from django.core.management.base import BaseCommand
from core.models import Quiz, Question

class Command(BaseCommand):
    help = 'Import quiz questions from CSV file'

    def handle(self, *args, **kwargs):
        with open('core/data/quiz_questions.csv', newline='', encoding='utf-8', errors='replace') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                quiz_title = row['Question'].split('?')[0]
                quiz, created = Quiz.objects.get_or_create(title=quiz_title)
                
                Question.objects.create(
                    quiz=quiz,
                    question_text=row['Question'],
                    option1=row['Option A'],
                    option2=row['Option B'],
                    option3=row['Option C'],
                    option4=row['Option D'],
                    correct_option=row['Correct Answer']
                )

        self.stdout.write(self.style.SUCCESS('Successfully imported quiz questions.'))
