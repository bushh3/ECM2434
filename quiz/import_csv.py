import csv
from quiz.models import Quiz, Question

def import_questions_from_csv():
    file_path = 'quiz/data/quiz_questions.csv'

    with open(file_path, newline='', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)

        next(csvreader)
        
        for row in csvreader:
            question_text = row[0]
            options = row[1:5] 
            correct_option = row[5]

            quiz, created = Quiz.objects.get_or_create(title="Default Quiz") 

            question = Question(
                quiz=quiz,
                question_text=question_text,
                option1=options[0],
                option2=options[1],
                option3=options[2],
                option4=options[3],
                correct_option=correct_option,
            )
            question.save()

    print("Questions imported successfully.")
