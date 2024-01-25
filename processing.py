import pandas as pd 
from pymongo import MongoClient




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

client = MongoClient("mongodb://localhost:27017/")  # Update with your MongoDB connection details
db = client["hackathon_coders"]
collection = db["questions"]

data2 = collection.find({})  

data = "data going to database"


for i in range(0,len(data)):
    if i%2 != 0:
        data['child_name'].iloc[i] = data['child_name'].iloc[i - 1]
data1 = data.copy()
data1 = data1.drop(data1.index[data1.index %2 == 0])
data1.reset_index(drop = True,inplace = True)
data1.drop("_id",axis = 1,inplace = True)
actual_columns = ["Name","Age"]
for i in range(2,len(data1.columns.values)):
    b = data1.columns.values[i].split('.')
    actual_columns.append(b[1])
existing_columns = data1.columns.values
column_name_mapping = {existing_column: new_column for existing_column, new_column in zip(existing_columns, actual_columns)}
data1 = data1.rename(columns = column_name_mapping)
for i in range(0,len(data1)):
    if data1['Age'].iloc[i] == 1:
        data1["Age"].iloc[i] = "0-12 months"
    elif data1["Age"].iloc[i] == 2:
        data1["Age"].iloc[i] = "1-3 years"
    elif data1["Age"].iloc[i] == 3:
        data1["Age"].iloc[i] = '3-6 years'
column_with_yes = []
for column in data1.columns:
    if data1[column].eq("No").any():
        column_with_yes.append(column)
disablityy = []
for disablity in column_with_yes:
    disablityy.append(disabilities[data1['Age'].values[0]][disablity])
print(column_with_yes)
print(disablityy)
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
    recomm_therapy.append(recommendations.get(new,"It requires doctor's assistance"))
pp = ''
for recc in recomm_therapy:
    if recomm_therapy.index(recc) == len(recomm_therapy) - 1:
        pp = pp + recc
    else:
        pp = pp + recc + ','
df['Recommended Therapy'] = pp
result = [df['Name'].iloc[0],df['Age'].iloc[0],df['Possible Disabilities'].iloc[0],df['Recommended Therapy'].iloc[0]]
