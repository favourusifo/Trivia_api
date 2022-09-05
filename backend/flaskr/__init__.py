import sys
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from ..models import setup_db, Question, Category, db

# setting questions per page to allow variation
PAGINATED_QUESTIONS_PER_PAGE = 10

#creating a helper method to paginate questions and improve user experience.
#implementing pagination using request arguments and sending back results to the frontend as needed.
# PAGINATING QUESTIONS:
        # accessing the request object from the argument object in flask because it's a dictionary
        # getting the value of the key, page.
        # if key doesn't exist, or client doesn't specify, default to 1, using .get() method
        # and specify the type as int.

def paginate_questions(request, selection):
    # accessing the request object from flask.
    # getting the value of the key, page.
    # if key doesn't exist, or client doesn't specify, default to 1, using .get() method
    # and specify the type as int.
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * PAGINATED_QUESTIONS_PER_PAGE
    end = start + PAGINATED_QUESTIONS_PER_PAGE

    #using list interpolation to appropriately format questions.
    questions = [question.format() for question in selection]

    # returning only the set of questions that I want the user to view in this specific request.
    current_questions = questions[start:end]
    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)


# Setting up CORS and allowing headers, content type. Setting authorization to true.
    CORS(app)
    cors = CORS(app, resources={r"/*": {"origins": "*"}})


# Here, I use the after_request decorator to set Access-Control-Allow
    @app.after_request
    def after_request(response):

        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers',
                             'GET, POST, PUT, PATCH, DELETE, OPTIONS')
        return response


# Here, I create an endpoint to GET my requests in ALL categories.

    @app.route("/categories")
    # basic request for categories. Default method, GET
    def get_all_categories():

        try:
            # querying categories to get all the category objects.
            categories = Category.query.order_by(Category.type).all()


            #displaying error 404 when there are no categories
            if len(categories) == 0:
                # abort if number of questions requested exceeds available questions.
                abort(404)

            #Building out the body of the JSON object.
            #displaying category id and type for each category.
            #setting a success value.
            return jsonify({
                'success': True,
                'categories': {category.id: category.type for category in categories}
            })

        except Exception as e:
            print("Sorry, your request returned an error.")
            abort(400)

            # postman/ terminal test => curl http://127.0.0.1:5000/categories
            # postman/ terminal result =>
            # {"categories": {"1": "Science", "2": "Art", "3": "Geography",
            # "4": "History", "5": "Entertainment",
            # "6": "Sports"}, "success": true}

# TO DO
# Creating an endpoint for handling GET requests for questions.
# Applying a page-based pagination to the "/questions" endpoint.
# implementing pagination using query parameters, ID, and sending back results to the frontend as needed.


    @app.route('/questions')
    def get_questions():
        # Getting information about all questions using only the default GET method
        selection = Question.query.order_by(Question.id).all()

        #current questions
        current_questions = paginate_questions(request, selection)

        #total questions
        total_questions = len(selection)

        if len(current_questions) == 0:
            abort(404)

        categories = Category.query.order_by(Category.type).all()


        return jsonify({
            'success': True,
            'categories': {str(cat.id): cat.type for cat in categories},
            'currentCategory': None,
            'questions': current_questions,
            'totalQuestions': total_questions
        })

# curl http://127.0.0.1:5000/questions
# shortened terminal response:
# {"categories":{"1":"Science", "2":"Art", "3":"Geography", "4":"History", "5":"Entertainment",
# "6":"Sports"}, "currentCategory":"Entertainment","questions":[{"answer":"Apollo 13","category":5


# ***** TO DO *****
# Endpoint has a variable name specifying a questions ID
# set the converter/ variable type to int.
# Endpoint will DELETE questions after inputting a question ID.
# passing question_id as a parameter to the method.
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):

        #making sure that questions exist
        try:

            question = Question.query.filter(Question.id == question_id).one_or_none()

            # abort 404 if no question
            if question is None:
                abort(404)

            #deleting question
            question.delete()

            #getting all questions ordered by ID
            selection = Question.query.order_by(Question.id).all()

            #implementing pagination for better user experience
            current_question = paginate_questions(request, selection)


            return jsonify({
                'success': True,
                'deleted': question_id,
                'total_questions': len(Question.query.all()),
                'questions': current_question
            })

        except:
            abort(422)


#*****TO DO******

#Creating an endpoint to POST a new question,
    @app.route('/questions', methods=['POST'])

    def create_question():
        body = request.get_json()

        # *****AS EXPLAINED IN THE UDACITY VIDEO LECTURE: LESSON 3 - REQUESTS SOLUTION *******

        question_addition = body.get('question', None)
        answer_addition = body.get('answer', None)
        difficulty_score = body.get('difficulty', None)
        category_addition = body.get('category', None)

        try:
            # adding the new question, answer, difficulty score, and category
            question = Question(question=question_addition, answer=answer_addition,
                                difficulty=difficulty_score, category=category_addition)

            #inserting question into the database
            question.insert()

            selection = Question.query.order_by(Question.id).all()
            available_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'added': question.id,
                'questions': available_questions,
                'total_questions': len(Question.query.all())
            })

        except:
            print("error")
            abort(422)


#*****TO DO****
#Creating a POST endpoint to get questions based on a search term.

    @app.route("/questions", methods=["POST"])
    def get():
        req_data = request.get_json()

        client_search = None

        if client_search in req_data:
            client_search = req_data['search_term']

        results = Question.query.filter(Question.question.ilike("%{}%".format(client_search)))

        # total questions
        total_questions = len(results)

        # formatted questions
        questions = [question.format() for question in results]

        return jsonify({
            'success': True,
            'questions': questions,
            'total_questions': total_questions,
            'current_category': None
        })


# TO DO:
# Creating a GET endpoint to get questions based on category.


    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def questions_category(category_id):

        try:
            questions = Question.query.filter(Question.category == str(category_id)).all()

            # formatting questions
            formatted_questions = [question.format() for question in questions]
            total_questions = len(questions)

            return jsonify({
                'success': True,
                'questions': formatted_questions,
                'total_questions': total_questions,
                'current_category': category_id
            })

        # abort if an error is raised
        except Exception as e:
            print("An error has been encountered")
            abort(404)


# ****TO DO***
# Creating a POST endpoint to get questions to play the quiz.

    @app.route('/quizzes', methods=['POST'])
    def quiz_time():
        global current_question
        try:
            body = request.get_json()

            # end game if there are no available questions
            if not ('previous_questions' in body and 'quiz_category' in body):
                abort(422)

            # endpoint takes the category parameter
            category = body.get("category", None)
            # endpoint takes the previous question parameter
            previous_questions = body.get('previous_questions', None)
            # getting category id from the quiz category
            category_id = category[id]
            # getting previous question id
            previous_id = previous_questions[id]


            while category_id:

                answered_question = []
                question_gap = 2

                # retrieving questions and excluding the previous question
                available_questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
                # randomizing the new question bank/ collection
                question_bank = random.randrange(available_questions, len(available_questions))
                # setting the current question
                current_question = question_bank
                # separating questions that have been answered
                answered_question.append(current_question)
                # proceeding to the next question which current question + 2
                current_question += question_gap

                # breaking the loop if there are no questions left.
                if len(available_questions) == 0:
                    break

            return jsonify({
                'success': True,
                'question': current_question
            })

        except Exception as e:
            print("error")
            abort(422)


# Create error handlers for all expected errors including 404 and 422.

    # error handler for error 404
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False,
                     "error": 404,
                     "message": "Error: Not found"}),
            404,
        )

    # error handler for error 422
    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False,
                     "error": 422,
                     "message": "Error: Request not processable"}),
            422,
        )

    # error handler for error 400
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        }), 400

    # error handler for error 405
    @app.errorhandler(405)
    def method_error(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "Error: Method not allowed"
        }), 405

    # error handler for error 500
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal Server Error"
        }), 500

    return app

