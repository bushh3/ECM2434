import csv
from django.core.management.base import BaseCommand
from quiz.models import Question, Quiz

class Command(BaseCommand):
    help = 'Import quiz questions from a CSV file'

    def handle(self, *args, **kwargs):
        file_path = 'quiz/data/quiz_questions.csv'

        quiz, created = Quiz.objects.get_or_create(title="Environmental Quiz")

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                question_text = row['Question']
                option_a = row['Option A']
                option_b = row['Option B']
                option_c = row['Option C']
                option_d = row['Option D']
                correct_answer = row['Correct Answer']

                question = Question.objects.create(
                    quiz=quiz, 
                    question_text=question_text,
                    option1=option_a,
                    option2=option_b,
                    option3=option_c,
                    option4=option_d,
                    correct_option=correct_answer
                )

                self.stdout.write(self.style.SUCCESS(f'Successfully imported question: "{question_text}"'))

