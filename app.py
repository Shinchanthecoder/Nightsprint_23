from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import pandas as pd

app = Flask(__name__)

# MongoDB configuration
mongo_uri = "mongodb://localhost:27017/"
client = MongoClient(mongo_uri)
db = client["hackathon_coders"]
collection = db["questions"]
recommendations = {
    "Vision problems": "Vision therapy,Orientation and mobility training,Braille instruction",
    "Attention deficit hyperactivity disorder (ADHD)": "Behavioral therapy,Medication management,Psychoeducation",
    "Cerebral palsy": "Physical therapy,Occupational therapy,Speech therapy",
    "Muscular dystrophy": "Physical therapy,Assistive devices,Respiratory therapy",
    "Other Motor Disabilities": "Physical and occupational therapy,Assistive technology",
    "Language delay": "Speech therapy,Early intervention services",
    "Autism spectrum sisorder": "ABA therapy,Speech and language therapy,Occupational therapy",
    "Cognitive disability": "Cognitive-behavioral therapy,Special education services",
    "Sensory Processing Disorder": "Sensory integration therapy",
    "Oral motor dysfunction": "Speech therapy,Occupational therapy",
    "Feeding disorder": "Feeding therapy",
    "Sleep disorder": "Sleep hygiene education,Behavioral therapy"
}
disabilities = {
    "0-12 months": {
        "Can your baby focus on moving objects?": ["Vision problems", "Attention deficit hyperactivity disorder (ADHD)"],
        "Can your baby follow objects with their eyes?": ["Vision problems", "Cerebral palsy"],
        "Can your baby reach for and grasp objects?": ["Cerebral palsy", "Muscular dystrophy", "Other motor disabilities"],
        "Can your baby transfer objects from one hand to the other?": ["Cerebral palsy", "Muscular dystrophy", "Other motor disabilities"],
        "Does your baby babble with different intonations?": ["Language delay", "Autism spectrum disorder"],
        "Does your baby understand the concept of object permanence?": ["Autism spectrum disorder", "Cognitive disability"],
        "Does your baby have difficulty calming down when upset?": ["Sensory processing disorder"],
        "Does your baby have difficulty feeding?": ["Oral motor dysfunction", "Feeding disorder"],
        "Does your baby have difficulty sleeping?": ["Sleep disorder"]
    },
    "1-3 years": {
        "Can your child understand and follow simple instructions, such as 'Get your ball' or 'Put on your shoes'?": ["Language delay", "Autism spectrum disorder", "Cognitive disability"],
        "Can your child use simple utensils, such as a spoon or fork?": ["Cerebral palsy", "Muscular dystrophy", "Other motor disabilities", "Oral motor dysfunction"],
        "Can your child dress themselves with help?": ["Cerebral palsy", "Muscular dystrophy", "Other motor disabilities", "Cognitive disability"],
        "Can your child identify common objects, such as a car, a ball, or a cat?": ["Language delay", "Autism spectrum disorder", "Cognitive disability"],
        "Can your child understand and use simple emotions, such as happy, sad, and angry?": ["Autism spectrum disorder", "Cognitive disability"],
        "Does your child have difficulty understanding or using language?": ["Language delay", "Autism spectrum disorder", "Specific language disorder"],
        "Does your child have difficulty interacting with other children?": ["Autism spectrum disorder", "Social communication disorder"],
        "Does your child have repetitive behaviors or interests?": ["Autism spectrum disorder"],
        "Does your child have difficulty controlling their emotions or behavior?": ["Attention deficit hyperactivity disorder (ADHD)", "Oppositional defiant disorder (ODD)", "Conduct disorder"],
        "Does your child have difficulty paying attention in school or completing tasks?": ["Attention deficit hyperactivity disorder (ADHD)", "Cognitive disability", "Learning disability"]
    },
    "3-6 years": {
        "Can your child follow simple stories with multiple steps?": ["Language delay", "Autism spectrum disorder", "Cognitive disability"],
        "Can your child answer simple questions about their day, such as 'What did you eat for lunch?' or 'Where did we go to play today?'": ["Language delay", "Autism spectrum disorder", "Cognitive disability"],
        "Can your child identify and name basic colors and shapes?": ["Language delay", "Autism spectrum disorder", "Cognitive disability", "Visual processing disorder"],
        "Can your child recognize and write their own name?": ["Language delay", "Autism spectrum disorder", "Cognitive disability", "Dyslexia"],
        "Can your child use simple pronouns, such as 'I,' 'me,' 'you,' and 'he/she/it'?": ["Language delay", "Autism spectrum disorder", "Cognitive disability"],
        "Can your child understand and follow more complex rules, such as 'Don't run in the house' or 'Wait your turn'?": ["Autism spectrum disorder", "Cognitive disability", "Attention deficit hyperactivity disorder (ADHD)", "ODD"],
        "Does your child have difficulty controlling their emotions or behavior?": ["Attention deficit hyperactivity disorder (ADHD)", "ODD", "Conduct disorder", "Emotional dysregulation disorder"],
        "Does your child have difficulty paying attention in school or completing tasks?": ["Attention deficit hyperactivity disorder (ADHD)", "Cognitive disability", "Learning disability"],
        "Does your child have difficulty reading or writing?": ["Learning disability", "Dyslexia"],
        "Does your child have difficulty with math?": ["Learning disability", "Dyscalculia"]
    }
}

def process_data(data):
    if "Age" not in data:
        data["Age"] = 25  # Add an "Age" column if not present

    # Your data processing code here
    data1 = data.copy()
    # data1.drop("_id", axis=1, inplace=True)
    actual_columns = ['Id', "Age"]
    for i in range(2, len(data1.columns.values) - 1):
        b = data1.columns.values[i].split('.')
        print(b[0],b)
        actual_columns.append(b[1])
    actual_columns.append('Name')
    existing_columns = data1.columns.values
    column_name_mapping = {existing_column: new_column for existing_column, new_column in zip(existing_columns, actual_columns)}
    data1 = data1.rename(columns=column_name_mapping)
    for i in range(0, len(data1)):
        if data1['Age'].iloc[i] == 1:
            data1["Age"].iloc[i] = "0-12 months"
        elif data1["Age"].iloc[i] == 2:
            data1["Age"].iloc[i] = "1-3 years"
        elif data1["Age"].iloc[i] == 3:
            data1["Age"].iloc[i] = '3-6 years'
    column_with_yes = data1.columns[data1.eq("No").any()]
    disablityy = []
    for disablity in column_with_yes:
        disablityy.append(disabilities[data1['Age'].values[0]][disablity])
    dissi = ""
    new_diss = []
    for dis in disablityy:
        for fa in dis:
            if dis.index(fa) == len(dis) - 1:
                dissi = dissi + fa
            else:
                dissi = dissi + fa + ','
            new_diss.append(fa)
    df = data1.copy()
    df['Possible Disabilities'] = dissi
    recomm_therapy = []
    for new in new_diss:
        recomm_therapy.append(recommendations.get(new, "It requires doctor's assistance"))
    pp = ''
    for recc in recomm_therapy:
        if recomm_therapy.index(recc) == len(recomm_therapy) - 1:
            pp = pp + recc
        else:
            pp = pp + recc + ','
    df['Recommended Therapy'] = pp
    result = [df['Age'].values[0], df['Possible Disabilities'].values[0], df['Recommended Therapy'].values[0]]
    return result

@app.route("/")
def front():
    return render_template("front.html")

@app.route("/index.html", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get user inputs from the form
        child_name = request.form.get("child_name")
        child_age = request.form.get("child_age")

        # Store child information in the database
        document = {
            "child_name": child_name,
            "child_age": child_age,
        }
       

        # Get the data from the database
       

        # Convert the data to a pandas DataFrame
       
        # Perform data processing
      

        # Redirect to a page to ask developmental milestone questions based on the child's age
        return redirect(url_for("ask_questions", child_age=child_age, child_name=child_name))

    # Handle the initial load of the page here
    return render_template("index.html")

@app.route("/ask_questions/<child_age>/<child_name>", methods=["GET", "POST"])
def ask_questions(child_age,child_name):
    if request.method == "POST":
        # Get the answers to developmental milestone questions from the form
        answers = request.form.to_dict()

        # Store child information, child_age, child_name, and answers in the database
        document = {
            "child_age": child_age,
            "answers": answers,
            "child_name":child_name,
        }
        collection.insert_one(document)

        # Perform data processing
        data = collection.find({})
        processed_data = process_data(pd.DataFrame([data]))

        # Redirect to a thank you page or another appropriate page
        return render_template("result.html", processed_data=processed_data)

    return render_template(f"questions{child_age}.html", child_age=child_age, child_name=child_name)

@app.route("/thank_you")
def thank_you():
    return "Thank you for submitting your responses!"

if __name__ == "__main__":
    app.run(debug=True)
